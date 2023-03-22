#!/usr/bin/env python
import csv
import os
import pprint
import sys
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = 'myhestia.settings'
sys.path.append('/var/www/myhestia')

try:
    # from Django 1.6 to 1.7, all scripts need to run setup(), otherwise, modules may not be ready.
    from django import setup
    setup()
except ImportError:
    setup = None

from cronjobs.common import log, end
from django.db import transaction
from django.db.models import Q
from clientdb.models import Client
from core.models import Staff
from matters.models import MatterRecord
from matters.common import update_matter_notifications


SCRIPT_NAME = 'LOAD_MATTER_CSV'


def main(file_name):
    """
    Column 1 and 2: Name of the Buyers (For cases with 2 names, you will see the second name on Colume 2, and I can change it later depending if you want them in one colume or two).
    Next columns: the addresses
    Then phone number and email
    Next dates are the exchange date.
    The stamp duty amount
    Then stamp duty due date
    For these matters, we only need to be able to Text and Email to client 30 days, 7 days and on the date when stamp duty due.
    """

    log(script_name=SCRIPT_NAME, level='INFO', msg='Start')

    # clean matter clients
    _cnt = 0
    with open(file_name, 'rb') as f:
        reader = csv.reader(f)

        with transaction.atomic():
            for line_idx, row in enumerate(reader):
                row = map(lambda it: it.strip(), row)
                matter_no = row[0]
                if not matter_no:
                    continue

                MatterRecord.objects.filter(matter_num=matter_no).delete()
                _cnt += 1

    log(script_name=SCRIPT_NAME, level='INFO', msg='Clean matter client done. [cnt]%s' % _cnt)

    _cnt = 0
    with open(file_name, 'rb') as f:
        reader = csv.reader(f)

        with transaction.atomic():
            for line_idx, row in enumerate(reader):
                _cnt += 1
                row = map(lambda it: it.strip(), row)

                # print row
                matter_no = row[0]
                # print matter_no
                if not row[1]:
                    continue

                customer_name_list = []
                for _c in row[1].split(' and'):
                    customer_name_list.extend(_c.split(','))

                customer_name_list = map(lambda it: it.strip(), customer_name_list)
                # print customer_name_list

                street1 = row[2]
                street2 = row[3]
                street_name = row[4]
                street = "%s%s%s%s" % (
                    street1 if street1 else '',
                    ', ' if street1 and street2 else '',
                    street2 if street2 else '',
                    ', ' + street_name if street_name else '')
                # print street

                suburb = row[5]
                state = row[6]
                postcode = row[7]

                mobile = row[8].replace(' ', '').replace('+', '')
                _idx = 0
                for _c in mobile:
                    if _c not in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'):
                        _idx += 1
                        continue
                    break
                mobile = mobile[_idx:]
                # print mobile

                email = row[9]
                # print email
                exchange_date = datetime.datetime.strptime(row[10], "%d/%m/%Y") if row[10] and row[10] != '00/00/00' else None
                duty_amount = row[11].replace('$', '').replace(',', '')
                duty_due_date = datetime.datetime.strptime(row[12], "%d/%m/%Y") if row[12] and row[12] != '00/00/00' else None
                # print exchange_date, duty_amount, duty_due_date

                old_matter = MatterRecord.objects.filter(matter_num=matter_no).first()
                matter = MatterRecord.objects.filter(matter_num=matter_no).first()
                if not matter:
                    matter = MatterRecord(matter_num=matter_no)

                admin = Staff.objects.get(email='cheryl@linklawyers.com.au')
                matter.matter_type = MatterRecord.TYPE_PURCHASE_OFF_PLAN
                matter.matter_admin = admin
                matter.property_street = street
                matter.property_suburb = suburb
                matter.property_state = state
                matter.property_postcode = postcode
                matter.solicitor_name = 'Phoebe Chow'
                matter.solicitor_email = 'pchow@linklawyers.com.au'
                matter.solicitor_mobile = '0410493872'
                matter.stamp_duty_amount = duty_amount
                matter.stamp_duty_due_date = duty_due_date
                matter.contract_exchange_date = exchange_date
                matter.created_by = admin
                matter.save()

                for _name in customer_name_list:
                    first_name = ' '.join(_name.split(' ')[:-1])
                    last_name = _name.split(' ')[-1]
                    client = Client.objects.filter(first_name=first_name, last_name=last_name,
                                                   email=email, mobile=mobile).first()
                    if not client:
                        client = Client(first_name=first_name, last_name=last_name, email=email, mobile=mobile)

                    client.save()

                    matter.clients.add(client)

                # notification
                update_matter_notifications(new_matter=matter, old_matter=old_matter)

    log(script_name=SCRIPT_NAME, level='INFO', msg='Completed. [cnt]%s' % _cnt)

    end(script_name=SCRIPT_NAME)

if __name__ == "__main__":

    argv = sys.argv[1:]

    if len(argv) != 1 or argv[0] == '':
        print "please input file name"
        exit(1)

    _file_name = argv[0]

    msg = 'Start. [file_name]%s' % _file_name
    log(script_name=SCRIPT_NAME, level='INFO', msg=msg)

    main(_file_name)
