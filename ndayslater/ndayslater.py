import email
from email.mime.text import MIMEText
import json
import configargparse
import imapclient
import datetime
import re
import asjson as json

import logging
logger=logging.getLogger(__name__)


def get_config_parser():
    config_parser = configargparse.ArgParser(default_config_files=['~/.config/ndayslater/ndayslater.conf'])
    config_parser.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
    config_parser.add('-o', '--host', required=True)
    config_parser.add('--port', required=False, default=None)
    config_parser.add('--no-ssl', required=False, default=False, action='store_true')
    config_parser.add('-u', '--user', required=True)
    config_parser.add('-p', '--password', required=True)
    config_parser.add('-v', '--verbose', action='store_true')
    config_parser.add('--name-of-base-folder', default='ndayslater')
    return config_parser

def main():
    config_parser=get_config_parser()
    args = config_parser.parse_args()
    if args.verbose:
        loglevel=logging.DEBUG
    else:
        loglevel=logging.INFO

    logging.basicConfig(level=loglevel)
    logger.debug('start')

    run(args)

class LastRun(object):

    mail_rfc822=None
    datetime_of_last_run=None
    attributes=set(['datetime_of_last_run'])

    def __init__(self, mail_rfc822):
        self.mail_rfc822=mail_rfc822
        msg = email.message_from_string(mail_rfc822)
        for part in msg.walk():
            payload=part.get_payload(decode=True)
            data=json.loads(payload)
            self.load_data(data)
            break
        if not self.datetime_of_last_run:
            raise ValueError('failed to initialize LastRun')

    def __unicode__(self):
        return '<%s %s>' % (self.__class__.__name__, self.datetime_of_last_run)

    def __repr__(self):
        return unicode(self).encode('ascii')

    def as_string(self):
        return self.mail_rfc822

    def load_data(self, data):
        seen=set()
        for key, value in data.items():
            if key not in self.attributes:
                logger.warn('unsupported key in data? %r %r' % (key, value))
                continue
            seen.add(key)
            setattr(self, key, value)
        if not seen==self.attributes:
            logger.warn('missing attributes during load_data(): attributes=%s seen=%s' % (self.attributes, seen))

    @classmethod
    def create_from_msg_id(cls, server, msgid):
        folder=server.args.name_of_base_folder
        server.select_folder(folder)
        mails=server.fetch([msgid], ['RFC822'])
        if len(mails)>1:
            logger.warn('more than one message found? %s' % mails)
        mail_rfc822=mails.values()[0]['RFC822']
        last_run=cls(mail_rfc822)
        logger.debug('last_run loaded from mail on server: %s' % last_run)
        return last_run

    @classmethod
    def create_from_scratch(cls, server, datetime_of_last_run=None):
        if not datetime_of_last_run:
            datetime_of_last_run=datetime.datetime.now()-datetime.timedelta(days=1)
        msg = MIMEText(json.dumps(dict(datetime_of_last_run=datetime_of_last_run)))
        msg['subject']=server.subject_of_status_mail
        return cls(msg.as_string())

class NDaysLaterIMAPClient(imapclient.IMAPClient):
    INBOX='INBOX'
    subject_of_status_mail='status_of_last_ndayslater_run'

    def __init__(self, args):
        self.args=args
        super(NDaysLaterIMAPClient, self).__init__(args.host, port=args.port, use_uid=True, ssl=not(args.no_ssl))

    def get_day_folder(self, day_as_int):
        return '%s/day%02d' % (self.args.name_of_base_folder, day_as_int)

    def get_plus_folder(self, plus_days_as_int):
        return '%s/plus%02d' % (self.args.name_of_base_folder, plus_days_as_int)

    def create_days_folders(self):
        self.get_or_create_folder(self.args.name_of_base_folder)
        for day_as_int in range(1, 32):
            self.get_or_create_folder(self.get_day_folder(day_as_int))
        self.get_or_create_folder(self.args.name_of_base_folder)

    def get_or_create_folder(self, folder_name):
        try:
            return self.select_folder(folder_name)
        except self.Error, exc:
            logger.warn(('creating folder %s' % folder_name))
            self.create_folder(folder_name)
            self.subscribe_folder(folder_name)
            return self.select_folder(folder_name)

    def move_today_to_inbox(self):
        today=datetime.date.today()
        return self.move_date_to_inbox(today)

    def move_date_to_inbox(self, date):
        day_folder=self.get_day_folder(date.day)
        self.move_mails_of_folder_to_other_folder(day_folder, self.INBOX)

    def move_mails_of_folder_to_other_folder(self, folder_name, other_folder):
        self.get_or_create_folder(folder_name)
        self.move(self.search(['NOT', 'DELETED']), other_folder, folder_name)

    def move(self, messages, folder, from_message='?'):
        logger.debug('moving %s messages from %s to %s' % (len(messages), from_message, folder))
        self.copy(messages, folder)
        self.add_flags(messages, [imapclient.DELETED])
        self.expunge()

    def update_to_layout_version_1(self):
        # update to new layout
        for flags, delim, folder_name in self.list_folders(self.args.name_of_base_folder):
            if not '/' in folder_name:
                continue
            new_name=re.sub(r'/d', '/day', folder_name)
            self.rename_folder(folder_name, new_name)
            self.subscribe_folder(new_name)

    def get_datetime_of_last_run_or_today(self):
        datetime_of_last_run=self.get_datetime_of_last_run_or_none()
        if datetime_of_last_run:
            return datetime_of_last_run


    def get_last_run(self):
        last_run=self.get_last_run_or_none()
        if last_run:
            return last_run
        return LastRun.create_from_scratch(self)

    def get_last_run_or_none(self):
        folder=self.args.name_of_base_folder
        self.select_folder(folder)
        try:
            msg_id=self.search(['SUBJECT', self.subject_of_status_mail])[0]
        except IndexError:
            logger.info('No mail with subject %r found. First run?' % self.subject_of_status_mail)
            return
        return LastRun.create_from_msg_id(self, msg_id)

    def set_last_run(self, now):
        logger.debug('setting last_run via status mail. Now: %s' % now)
        self.delete_old_last_status_mail()
        last_run=LastRun.create_from_scratch(self, now)
        self.append(self.args.name_of_base_folder, last_run.as_string())

    def delete_old_last_status_mail(self):
        folder=self.args.name_of_base_folder
        self.select_folder(folder)
        self.add_flags(self.search(['SUBJECT', self.subject_of_status_mail]), [imapclient.DELETED])
        self.expunge()

def move_mails_from_plus_folders_to_day_folders(last_run, now, server):
    for plus_days in range(1, 29):
        folder_name=server.get_plus_folder(plus_days)
        server.get_or_create_folder(folder_name)
        to_datetime=last_run.datetime_of_last_run+datetime.timedelta(days=plus_days)
        to_folder=server.get_day_folder(to_datetime.day)
        server.move_mails_of_folder_to_other_folder(folder_name, to_folder)

def move_mails_from_day_folders_to_inbox(last_run, now, server):
    day_of_step=last_run.datetime_of_last_run.date()
    while day_of_step<=now.date():
        server.move_date_to_inbox(day_of_step)
        day_of_step=day_of_step+datetime.timedelta(days=1)


def run(args):
    server = NDaysLaterIMAPClient(args)
    server.login(args.user, args.password)

    server.create_days_folders()
    last_run=server.get_last_run()
    now=datetime.datetime.now()
    yesterday=now-datetime.timedelta(days=1)
    if last_run.datetime_of_last_run.date()>now.date():
        logger.warn('last run in the future? last_run=%s now=%s' % (last_run, now))
        last_run.datetime_of_last_run=yesterday
    delta_since_last_run = now - last_run.datetime_of_last_run
    if delta_since_last_run > datetime.timedelta(days=31):
        logger.warn('last run is very old. I ignore this old value: last_run=%s now=%s' % (last_run, now))
        last_run.datetime_of_last_run=yesterday
    move_mails_from_plus_folders_to_day_folders(last_run, now, server)
    move_mails_from_day_folders_to_inbox(last_run, now, server)
    server.set_last_run(now)
    logger.debug('done')


if __name__=='__main__':
    main()

