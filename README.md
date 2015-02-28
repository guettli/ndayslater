# ndayslater
Shedule mails for resubmission N days later

you have two choices if you read an email:

 - do it now
 - do it later

Sooner or later your inbox contains about one hundred "do it later" mails.

Everyday you see this huge list, you waste mental energy by skipping of the "do it later" mails.

You feel bad, since there is still so much to do.

Delay them, schedule them for resubmission N days later!

Keep your inbox clean: empty it daily.

No problem if something was not done today: Do it N days later :-)

This script creates a simple folder structure like this in your IMAP email box:

```
ndayslater/day01/ # --> first day of a month
ndayslater/day02/
...
ndayslater/day31/
```
If today is the first march, and you want to handle not today, but maybe in three days. Move the mail with our favorite mail user agent (thunderbird, outlook, k9 for android, ...) to ndayslater/day04/.

On 4th march the script moves all mails in the folder ndayslater/day04/ to your inbox again.

This way you can schedule mails for resubmission for about one month.

If you use the mail user agent thunderbird, then the following plugins are handy:

https://addons.mozilla.org/de/thunderbird/addon/nostalgy/ Nostalgy: quick moving of mails: Just hit "S y04 RETURN" to save a message to the next 4th day of the month.

https://addons.mozilla.org/de/thunderbird/addon/edit-email-subject/ Edit Email Subject: This plugin allows you to edit the subject of an message. This is handy if you want to make some note  on the mail. BTW, if you know a better way to make notes "on" mails, please let me know!






