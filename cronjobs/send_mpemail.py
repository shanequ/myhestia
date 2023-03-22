#!/usr/bin/python

"""
Send Multipart Emails

"""


import datetime
import os
import sys


sys.path.append('/var/www/myhestia')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myhestia.settings")

try:
    from django import setup
    setup()
except ImportError:
    setup = None

from django.db.models import Q

from messaging.models import MPEmail
from messaging.sending_email import send_email_via_ses

BATCH_SIZE = 100


def main():

    # ensure single entry to this cronjob
    from tendo import singleton
    _ = singleton.SingleInstance()

    print '--- %s starts at %s' % (__file__, datetime.datetime.now())

    query_cond = Q(status='P') | (Q(status='F') & Q(failure_count__lt=MPEmail.RETRY_LIMIT))
    email_list = MPEmail.objects.filter(query_cond)
    total = email_list.count()
    email_list = email_list[:BATCH_SIZE]

    count = send_email_via_ses(email_list)
    print '--- sent out %d emails successfully (total: %d)' % (count, min(BATCH_SIZE, total))


if __name__ == '__main__':
    main()
