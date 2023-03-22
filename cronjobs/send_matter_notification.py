#!/usr/bin/env python
import datetime
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myhestia.settings")
sys.path.append('/var/www/myhestia')

try:
    # from Django 1.6 to 1.7, all scripts need to run setup(), otherwise, modules may not be ready.
    from django import setup
    setup()
except ImportError:
    setup = None

from cronjobs.common import log, end
from matters.models import MatterNotification
from my_tools.message import MyNotice
from n_template.common import NConst
from myhestia.global_const import ALL_CC_EMAILS
from n_template.models import NReceiver

SCRIPT_NAME = 'MATTER_NOTIFICATION'


def main():
    """

    """
    now = datetime.datetime.now()
    log(script_name=SCRIPT_NAME, level='INFO', msg='Start')

    # matter notifications
    mns = MatterNotification.objects.filter(status=MatterNotification.STATUS_WAITING, expect_sent_at__lte=now)
    send_cnt = 0
    for mn in mns:
        # if no doc is as attachment, DO NOT sent
        if mn.get_missed_docs():
            continue

        if mn.send_type == NConst.SEND_TYPE_EMAIL:
            # email
            to_emails = mn.get_send_to_emails()
            cc_emails = mn.get_send_cc_emails()

            # all emails cc to info@...com.au
            if ALL_CC_EMAILS:
                cc_emails += ALL_CC_EMAILS

            attach_global_files = mn.get_attach_global_files()

            MyNotice.send_email(to_emails=to_emails, subject=mn.subject, template=mn.content,
                                cc_emails=cc_emails, attach_global_files=attach_global_files, mn=mn)

        elif mn.send_type == NConst.SEND_TYPE_SMS:
            # sms
            mobiles = mn.get_sms_mobiles()
            MyNotice.send_sms(mobiles=mobiles, sms_text=mn.content, mn=mn)

            # if admin, send email
            _to_emails = []
            for _to in mn.send_tos.all():
                if _to.receiver == NReceiver.RECEIVER_STAFF and mn.matter.matter_admin:
                    _to_emails.append(mn.matter.matter_admin.email)

            if _to_emails:
                _subject = "%s. [matter_num]%s" % (mn.get_trigger_desc(), mn.matter.matter_num,)
                MyNotice.send_email(to_emails=_to_emails, subject=_subject, template=mn.content, mn=mn)

            # send all sms as email to info@...com.au
            if ALL_CC_EMAILS:
                _subject = "SMS cc to email. [matter_num]%s" % mn.matter.matter_num
                MyNotice.send_email(to_emails=ALL_CC_EMAILS, subject=_subject, template=mn.content, mn=mn)

        MatterNotification.objects.filter(pk=mn.pk).update(sent_at=now, status=MatterNotification.STATUS_SENT)
        send_cnt += 1

    msg = 'Completed. [send_cnt]%s [read_cnt]%s' % (send_cnt, len(mns) if mns else 0,)
    log(script_name=SCRIPT_NAME, level='INFO', msg=msg)

    end(script_name=SCRIPT_NAME)

if __name__ == "__main__":
    from tendo import singleton
    _ = singleton.SingleInstance()
    main()
