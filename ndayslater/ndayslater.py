import configargparse
import imapclient
import datetime


def main():
    config_parser = configargparse.ArgParser(default_config_files=['~/.config/ndayslater'])
    config_parser.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
    config_parser.add('-o', '--host', required=True)
    config_parser.add('-u', '--user', required=True)
    config_parser.add('-p', '--password', required=True)
    config_parser.add('--name-of-base-folder', default='ndayslater')

    args = config_parser.parse_args()
    run(args)

class NDaysLaterIMAPClient(imapclient.IMAPClient):
    INBOX='INBOX'
    def __init__(self, args):
        self.args=args
        super(NDaysLaterIMAPClient, self).__init__(args.host, use_uid=True, ssl=True)

    def create_days_folders(self):
        self.get_or_create_folder(self.args.name_of_base_folder)
        for day_number in range(1, 32):
            self.get_or_create_folder('%s/%s' % (self.args.name_of_base_folder, day_number))
        self.get_or_create_folder(self.args.name_of_base_folder)

    def get_or_create_folder(self, folder_name):
        try:
            return self.select_folder(folder_name)
        except self.Error, exc:
            self.create_folder(folder_name)
            return self.select_folder(folder_name)

    def move_today_to_inbox(self):
        today=datetime.date.today()
        return self.move_date_to_inbox(today)

    def move_date_to_inbox(self, date):
        folder='%s/%s' % (self.args.name_of_base_folder, date.day)
        self.get_or_create_folder(folder)
        self.move(self.search(['NOT DELETED']), self.INBOX)

    def move(self, messages, folder):
        self.copy(messages, folder)
        self.add_flags(messages, [imapclient.DELETED])
        self.expunge()

def run(args):
    server = NDaysLaterIMAPClient(args)
    server.login(args.user, args.password)
    #server.create_days_folders()
    server.move_today_to_inbox()