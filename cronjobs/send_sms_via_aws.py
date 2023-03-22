#!/usr/bin/python

import boto3
import datetime
import os
import sys
from tendo import singleton


sys.path.append('/var/www/myhestia')
os.environ['DJANGO_SETTINGS_MODULE'] = 'myhestia.settings'

try:
    # from Django 1.6 to 1.7, all scripts need to run setup(),
    # otherwise, modules may not be ready.
    from django import setup
    setup()
except ImportError:
    setup = None


from messaging.models import SMS
from messaging.sms import wash_mobile_numbers


class AwsSMS(object):

    MAX_SMS_NUM = 100

    def __init__(self, sms_list, sender_id='LinkLawyer'):
        if not sms_list:
            raise ValueError('no SMS')

        super(AwsSMS, self).__init__()
        self.failure_count = 0
        self.success_count = 0
        self.sms_list = sms_list
        self.client = boto3.client('sns')
        self.message_attrs = {
            'AWS.SNS.SMS.SenderID':
                {'DataType': 'String', 'StringValue': sender_id}
        }

    def _send_sms(self, sms_text, target_list):

        for phone in target_list:
            self.client.publish(
                PhoneNumber=phone,
                Message=sms_text,
                MessageAttributes=self.message_attrs
            )

    def send(self):
        for sms in self.sms_list[:self.MAX_SMS_NUM]:
            target_list, err_list = wash_mobile_numbers(sms.target_numbers)
            if err_list:
                sms.note = 'incorrect target numbers: %s.' % err_list
            if not target_list:
                sms.note += ' No valid target numbers.'
                sms.status = 'C'
                sms.save()
                self.failure_count += 1
                return

            self._send_sms(sms.sms_text, target_list)
            sms.status = 'S'
            sms.save()
            self.success_count += 1


def main():

    _ = singleton.SingleInstance()
    print '\n\n--- %s starts at %s' % (__file__, datetime.datetime.now())

    sms_list = SMS.objects.filter(status='P')
    if not sms_list.exists():
        print '  No SMS to send'
        print '--- completed.'
        return
    else:
        print '  %s SMSs to send' % sms_list.count()
        aws_sms = AwsSMS(sms_list)
        aws_sms.send()

    print '--- completed at %s.  S: %d   F: %d' % (
        datetime.datetime.now(),
        aws_sms.success_count,
        aws_sms.failure_count
    )


if __name__ == '__main__':
    main()
