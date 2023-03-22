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
from n_template.models import NTemplate

SCRIPT_NAME = 'UPDATE_NOTIFICATION'


def main():
    """
        Inactivate old notification and new generate notification to use new template
    """
    log(script_name=SCRIPT_NAME, level='INFO', msg='Start')

    # matter notifications
    new_template_created_at = '2019-07-04 00:00:00'
    mns = MatterNotification.objects.filter(status=MatterNotification.STATUS_WAITING,
                                            is_manual=False,
                                            template_category=NTemplate.CATEGORY_MATTER_PURCHASE_OFF_PLAN,
                                            template_trigger=NTemplate.TRIGGER_STAMP_DUTY_DUE,
                                            template_trigger_days__in=[0, -10, -30])
    cnt = 0
    for mn in mns:
        MatterNotification.objects.filter(pk=mn.pk).update(content=mn.template.content)
        cnt += 1

        log(script_name=SCRIPT_NAME, level='INFO', msg='[idx]%s [pk]%s' % (cnt, mn.pk))

    end(script_name=SCRIPT_NAME)

if __name__ == "__main__":
    from tendo import singleton
    _ = singleton.SingleInstance()
    main()
