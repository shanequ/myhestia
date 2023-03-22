

import boto
import boto3
from boto.exception import BotoServerError, BotoClientError, NoAuthHandlerFound
import boto.ses

import logging
import os

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart


from myhestia.global_const import (
    AWS_SES_REGION, EMAIL_DOMAIN, ADMIN_EMAIL, NOTICE_BU_NAME, USE_AWS_BOTO3
)


def _aws_get_ses_client():
    """Use boto3 to get a SES client object"""
    try:
        return boto3.client('ses', region_name=AWS_SES_REGION)
    except Exception as e:
        print 'get boto3 client: {}'.format(e)
        return None


def aws_get_ses_connection():
    """Connect to SES Service."""

    if USE_AWS_BOTO3:
        return _aws_get_ses_client()

    try:
        return boto.ses.connect_to_region(AWS_SES_REGION)
    except NoAuthHandlerFound, e:
        print 'Error to connect to SES: %s' % e
        return None


def aws_send_ses_email(email, conn=None):
    """Send Outgoing Multipart Email via Amazon SES Service."""

    logging.getLogger('boto').setLevel(logging.INFO)

    msg = MIMEMultipart()
    msg['Subject'] = email.subject

    if email.from_email:
        from_email = email.from_email.strip()
    else:
        from_email = ''

    if not from_email:
        email.no_reply = True

    if email.no_reply:
        msg['From'] = '%s <%s>' % (NOTICE_BU_NAME, ADMIN_EMAIL,)
    else:
        msg['From'] = '%s <%s>' % (email.from_email_desc or from_email.split('@')[0], from_email)

    to_email_list = email.to_email.replace(',', ' ').replace(';', ' ').split()

    # no need to send out email if no recipient is given
    if not to_email_list:
        email.status = 'C'
        email.failure_log = 'No recipients'
        email.save()
        return

    if email.cc_email:
        cc_email = email.cc_email.replace(',', ' ').replace(';', ' ').split()
        msg['Cc'] = ','.join(cc_email)
        to_email_list += cc_email

    if email.bcc_email:
        msg['Bcc'] = email.bcc_email

    msg.preamble = 'Multipart Email Message from %s.\n' % EMAIL_DOMAIN

    if email.text_content:
        msg.attach(MIMEText(email.text_content, 'plain', 'utf-8'))
    if email.html_content:
        msg.attach(MIMEText(email.html_content, 'html', 'utf-8'))
    if email.reply_to:
        msg.add_header('reply-to', email.reply_to)

    # add file attachments, the file path may be separated by comma or semi-column
    file_paths = []
    if email.attach_file_list:
        file_paths = email.attach_file_list.replace(',', ' ').replace(';', ' ').split()

    for f in file_paths:
        if not os.path.isfile(f):
            continue
        print '  %s: Open file %s (%d) to attach ...' % (os.path.realpath(__file__), f, os.path.getsize(f))
        attach_part = MIMEApplication(open(f, 'rb').read())

        try:
            # /var/www/xxx.doc/matter_contract/1/05ac62e34df546d7896e247378a95043.pdf
            _type_name = f.split('/')[4]
            _ext = f.split('.')[-1]
            _file_name = "%s.%s" % (_type_name, _ext,)
        except IndexError:
            _file_name = os.path.basename(f)

        attach_part.add_header('Content-Disposition', 'attachment', filename=_file_name)
        msg.attach(attach_part)
        print '     attached.'

    # attach images, the file path may be separated by comma or semi-column
    file_paths = []
    if email.image_list:
        file_paths = email.image_list.replace(',', ' ').replace(';', ' ').split()

    for f in file_paths:
        if not os.path.isfile(f):
            continue

        print '  %s: Open image %s (%d) to attach ...' % (os.path.realpath(__file__), f, os.path.getsize(f))
        fp = open(f, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        img.add_header('Content-ID', '<%s>' % os.path.basename(f))
        msg.attach(img)

    if not conn:
        conn = aws_get_ses_connection()

    if not conn:
        raise ValueError('cannot connect to SES')

    error_flag = False
    result = []
    try:
        msg['To'] = ','.join(to_email_list)
        print '  sending email to %s ...' % to_email_list

        if USE_AWS_BOTO3:
            conn.send_raw_email(RawMessage={'Data': msg.as_string()})
        else:
            conn.send_raw_email(msg.as_string())

        result.append('sent to %s OK' % to_email_list)
        print '  sent successfully to %s.' % to_email_list
    except (BotoServerError, BotoClientError), e:
        error_flag = True
        result.append('failed to send to %s: %s' % (to_email_list, e))
        print '  failed to send to %s ...' % to_email_list

    if error_flag:
        email.failed()
    else:
        email.sent()

    email.failure_log = '|'.join(result)[:510]
    print '  status: %s' % email.get_status_display()
    email.save()
