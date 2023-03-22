from __future__ import unicode_literals

import datetime

from myhestia.settings import STATIC_URL

VERSION = '1.0.0'

THUMBNAIL_SIZE = (100, 100)
MD_THUMBNAIL_SIZE = (400, 400)

#
# website setting
#
WEBSITE_LOGO_URL = STATIC_URL + 'images/logo.png'
WEBSITE_BU_NAME = 'Link Lawyer'

#
# maximum organization tree level depth
#
# Team - Executive Management (level-0) -> Level-1 Team -> Level-2 Team
# Staff - CEO -> Team Head -> Sub-team Head -> Member
#
MAX_ORG_LEVEL = 3

#
# Notification
#
DEFAULT_NOTIFICATION_SENT_TIME = datetime.time(17, 0)

STUMP_DUTY_CHEQUE_PROVIDED_DAYS_BEFORE_DUE_DATE = 5

# official website url - email footer
OFFICIAL_URL = 'http://www.linklawyers.com.au'

# email header logo
OFFICIAL_LOGO_URL = 'http://linklawyer.myhestia.com.au/static/images/logo.png'

OFFICIAL_ADDRESS = '902/263-265 Castlereagh St, Sydney NSW 2000'
OFFICIAL_PHONE = '(02) 9212 0955'
OFFICIAL_FAX = '(02) 9212 0955'

# email subject, sms sender
NOTICE_BU_NAME = WEBSITE_BU_NAME

# email
AWS_SES_REGION = 'us-west-2'
USE_AWS_BOTO3 = True
EMAIL_DOMAIN = "linklawyers.com.au"
# EMAIL_DOMAIN must be verified by Amazon SES
ADMIN_EMAIL = 'info@' + EMAIL_DOMAIN
ACCOUNTING_EMAIL = 'account@' + EMAIL_DOMAIN

# all emails have a copy to cc to
ALL_CC_EMAILS = ['info@linklawyers.com.au']

# repeatable and will not send out
EXCEPTION_MOBILE = '00000000'
# repeatable and will send out
EXCEPTION_EMAIL = 'pchow@linklawyers.com.au'
