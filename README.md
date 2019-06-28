# ndayslater

This project is dead. Here is a more detailed documentation of the "n days later method": https://github.com/guettli/n-days-later-method

Schedule mails for resubmission N days later

you have two choices if you read an email:

 - do it now
 - do it later

Sooner or later your inbox contains about one hundred "do it later" mails.

Everyday you see this huge list, you waste mental energy by skipping of the "do it later" mails.

You feel bad, since there is still so much to do.

Delay them, schedule them for resubmission N days later!

Keep your inbox clean: empty it daily.

This script creates a simple folder structure like this in your IMAP email box:

```
ndayslater/day01/ # --> first day of a month
ndayslater/day02/
...
ndayslater/day31/ # --> only for January, March, May, July, August, October and December 
```
If today is the first march, and you want to handle a mail not today, but maybe in three days. Move the mail with our favorite mail user agent (thunderbird, outlook, k9 for android, ...) to the folder `ndayslater/day04/`.

On 4th march the script moves all mails in the folder `ndayslater/day04/` to your inbox again.

This way you can schedule mails for resubmission for about one month.

#Install

```
 pip install git+https://github.com/guettli/ndayslater.git#egg=ndayslater
```
 
#Configuration

```
# ~/.config/ndayslater/ndayslater.conf
host = example.com
user = foouser
password = 12345
```

# Running it daily
Use cron or a different sheduler to run the command at least once a day:

```
user@host> crontab -e

@daily ndayslater
```

# What ndayslater is not

It is not calender application. It is not intended for fixed dates like "On day X, Meeting with person Y in location Z". The ndayslater tools is intended for things you want to do, but it does not matter if you do it later.


# Limitations

Up to now, you can only move a message 31 days ahead. You can't schedule the mails to a month.

But forking this project is allowed and encouraged! Go ahead, improve it!

Tell me what you want to be improved. Please create an issue and explain what you think.


# Misc

Related: http://en.wikipedia.org/wiki/Tickler_file also known as 43Folders

If you use the mail user agent thunderbird, then the following plugins are handy:

https://addons.mozilla.org/de/thunderbird/addon/nostalgy/ Nostalgy: quick moving of mails: Just hit "S y04 RETURN" to save a message to the next 4th day of the month.

https://addons.mozilla.org/de/thunderbird/addon/edit-email-subject/ Edit Email Subject: This plugin allows you to edit the subject of an message. This is handy if you want to make some note  on the mail. BTW, if you know a better way to make notes "on" mails, please let me know!






