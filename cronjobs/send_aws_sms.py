#!/usr/bin/python
import boto3
import datetime
import os
import sys
import tendo
import urllib

sys.path.append('/var/www/myhestia')
os.environ['DJANGO_SETTINGS_MODULE'] = 'myhestia.settings'

try:
    # from Django 1.6 to 1.7, all scripts need to run setup(), otherwise, modules may not be ready.
    from django import setup

    setup()
except ImportError:
    setup = None

from tendo import singleton

from messaging.models import SMS
from messaging.sms import wash_mobile_numbers


MAX_BATCH_SIZE = 100


def main():
    # get list of pending SMS
    sms_list = SMS.objects.filter(status='P')[:100]

    snsc = boto3.client(
        'sns',
        aws_access_key_id='AKIAIK77AK6X4ZFR2TTQ',
        aws_secret_access_key='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',
        region_name='ap-southeast-2'
    )

    # ensure single entry to this cronjob
    _ = tendo.singleton.SingleInstance()
    print '--- %s starts at %s' % (__file__, datetime.datetime.now())

    s_count = 0
    f_count = 0
    print '   total SMS in this batch: %s' % sms_list.count()

    for sms in sms_list:
        failed = False
        # Triple encode the text
        # body_text = urllib.quote(sms.sms_text.encode('utf8'))
        # body_text = urllib.quote(body_text)
        body_text = sms.sms_text.encode('utf8')

        valid_targets, dirty_targets = wash_mobile_numbers(sms.target_numbers)
        print '    SMS ID: %s, valid targets: %s' % (sms.pk, valid_targets)
        sms.sp_response = 'SNS: '
        for t in valid_targets:
            if not t.startswith('+'):
                t = '+' + t
            print 'target: %s' % t

            try:
                rsp = snsc.publish(
                    PhoneNumber=t,
                    Message=body_text,
                    MessageAttributes={
                        'AWS.SNS.SMS.SenderID': {
                            'DataType': 'String',
                            'StringValue': 'LinkLawyer'
                        }
                    }
                )
            except Exception, e:
                sms.status = 'F'
                print e
                sms.save()
                failed = True
                f_count += 1
                break

            # get result
            result = rsp.get('ResponseMetadata', {}).get('HTTPStatusCode', 0)
            if result == 200:
                sms.sp_response += 'O'
            else:
                sms.sp_response += 'X'

        if not failed:
            s_count += 1
            sms.status = 'S'
            sms.save()

    print '--- completed. S: %d   F: %d' % (s_count, f_count)


if __name__ == '__main__':
    main()

