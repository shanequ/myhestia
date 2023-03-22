#!/usr/bin/python
import sys
import os
import tendo
import urllib2
import datetime


sys.path.append('/var/www/myhestia')
os.environ['DJANGO_SETTINGS_MODULE'] = 'myhestia.settings'

try:
    # from Django 1.6 to 1.7, all scripts need to run setup(), otherwise, modules may not be ready.
    from django import setup
    setup()
except ImportError:
    setup = None


from messaging.models import SMS
from messaging.sms import create_api_request


def main():

    # ensure single entry to this cronjob
    from tendo import singleton
    _ = tendo.singleton.SingleInstance()
    print '--- %s starts at %s' % (__file__, datetime.datetime.now())

    # get list of pending SMS
    sms_list = SMS.objects.filter(status='P')

    s_count = 0
    f_count = 0
    for sms in sms_list:
        api_req = create_api_request(sms)
        if not api_req:
            continue

        try:
            rsp = urllib2.urlopen(api_req, timeout=30)
        except urllib2.URLError, e:
            print '(%s) %d -- %s' % (str(datetime.datetime.now()), sms.id, e.reason)
            sms.note += e.reason[:127]
            sms.status = 'F'
            sms.save()
            f_count += 1
            break
        except Exception, e:
            print '(%s) %d -- %s' % (str(datetime.datetime.now()), sms.id, str(e))
            sms.note += type(e).__name__[:127]
            sms.status = 'F'
            sms.save()
            f_count += 1
            break

        sms.sp_response = rsp.read()
        if sms.sp_response[0:2] == 'OK':
            sms.status = 'S'
            s_count += 1
        else:
            sms.status = 'F'
            f_count += 1

        if len(sms.sp_response) > 126:
            sms.sp_response = sms.sp_response[:126]

        sms.save()

    print '--- completed. S: %d   F: %d' % (s_count, f_count)


if __name__ == '__main__':
    main()
