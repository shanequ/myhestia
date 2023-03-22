"""
Sending Email
"""

import os
import smtplib
import time

from django.core.mail import EmailMessage
from django.core.mail.backends import smtp

from .ses_email import aws_get_ses_connection, aws_send_ses_email

BOTO_USER = 'shanequ'
MAX_EMAIL_BATCH_SIZE = 100
MAX_EMAIL_BATCH_TIME = 90
EMAIL_BACKEND = 'AWS_SES'


def send_email_via_ses(email_list):
    """Send all emails in the list vis SES service."""

    # get a connection for sharing with multiple email sending
    conn = aws_get_ses_connection()
    if not conn:
        print '  cannot connect to SES service. Abort.\n'
        return 0

    email_count = 0
    t1 = time.time()

    for email in email_list:
        if email_count >= MAX_EMAIL_BATCH_SIZE:
            break

        email_count += 1
        print '  processing email %s ... ' % email.id
        aws_send_ses_email(email, conn)
        print 'done.\n'

        # sleep for a small amount time to avoid exceed the SES sending limit
        if email_count % 5 == 0:
            t2 = time.time()
            if t2 - t1 < 1:
                time.sleep(0.6)
            t1 = t2

    return email_count
