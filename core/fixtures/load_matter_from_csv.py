from __future__ import unicode_literals
import csv
import decimal
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'myhestia.settings'
sys.path.append('/var/www/myhestia')

try:
    # from Django 1.6 to 1.7, all scripts need to run setup(), otherwise, modules may not be ready.
    from django import setup
    setup()
except ImportError:
    setup = None

from django.db import transaction
from cronjobs.common import log
from core.models import Staff
from matters.models import MatterRecord
from django.db.models import Q
from myhestia.global_const import EXCEPTION_MOBILE
from clientdb.models import Client
SCRIPT_NAME = 'LOAD_CSV'
MATTER_CSV_FIELDS = ['Project', 'Ref. No', 'Purchaser', 'Client 1 MP', 'Client 1 Email',
                     'Client 2 MP', 'Client 2 Email', 'Unit No', 'Lot No', 'Address', 'Suburb', 'Post code']


def main(file_name, cli_run=True):

    sysadmin = Staff.objects.get(username='sysadmin')
    staff = Staff.objects.get(username='cheryl')

    total_rows = 0
    csv_reader = None
    try:
        # open input file
        if cli_run:
            csvfile = open(file_name, 'rU')
        else:
            csvfile = file_name
        csv_reader = csv.DictReader(csvfile)
        if csv_reader.fieldnames != MATTER_CSV_FIELDS:
            raise ValueError('Incorrect fields given: %s<br> Expected fields: %s' %
                             (',&nbsp;&nbsp;'.join(csv_reader.fieldnames), ',&nbsp;&nbsp;'.join(MATTER_CSV_FIELDS)))
    except ValueError, e:
        if cli_run:
            print e
        else:
            return False, str(e)
    except csv.Error, e:
        if cli_run:
            print e
        else:
            return False, 'CSV File format error. Expected CSV fields: %s' % \
                   ',&nbsp;&nbsp;'.join(MATTER_CSV_FIELDS)

    for row in csv_reader:
        total_rows += 1
        matter_number = row['Ref. No'].strip()

        if cli_run:
            print 'Start. [row]%s [ref.no]%s' % (total_rows, matter_number)

        unit_no = row['Unit No'].strip()
        lot_no = row['Lot No'].strip()
        purchaser_name = row['Purchaser'].strip()
        client1_mobile = row['Client 1 MP'].strip().replace(' ', '')
        client1_email = row['Client 1 Email'].strip()
        client2_mobile = row['Client 2 MP'].strip().replace(' ', '')
        client2_email = row['Client 2 Email'].strip()

        street = row['Address'].strip()
        suburb = row['Suburb'].strip()
        postcode = row['Post code'].strip()

        client1_name = purchaser_name
        client2_name = ''
        if 'and' in purchaser_name:
            names = purchaser_name.split('and')
            client1_name = names[0].strip()
            client2_name = names[1].strip()

        with transaction.atomic():
            matter = MatterRecord()

            matter.matter_num = matter_number
            matter.matter_type = MatterRecord.TYPE_PURCHASE_OFF_PLAN
            matter.matter_admin = staff
            matter.property_street = "%s, %s, %s" % (unit_no, lot_no, street)
            matter.property_suburb = suburb
            matter.property_postcode = postcode
            matter.property_state = 'NSW'

            matter.solicitor_name = 'Phoebe Chow'
            matter.solicitor_email = 'pchow@linklawyers.com.au'
            matter.solicitor_mobile = '0410493872'
            matter.created_by = sysadmin
            matter.save()

            if client1_name:
                client = Client.objects.filter(Q(email=client1_email)|Q(mobile=client1_mobile)).first()
                if not client:
                    client = Client()
                    client.first_name, client.last_name = split_name(client1_name)
                    client.email = client1_email
                    client.mobile = client1_mobile
                    client.save()
                    if cli_run:
                        print 'new client: %s, %s' % (client.first_name, client.last_name)
                matter.clients.add(client)

            if client2_name:
                client = None
                if client2_mobile:
                    client = Client.objects.filter(mobile=client2_mobile).first()

                if not client and client2_email:
                    client = Client.objects.filter(email=client2_email).first()

                if not client:
                    client = Client()
                    client.first_name, client.last_name = split_name(client2_name)
                    client.email = client2_email if client2_email else '%s@LINKLAWYERS.COM.AU' % matter_number
                    client.mobile = client2_mobile if client2_mobile else EXCEPTION_MOBILE
                    client.save()
                    if cli_run:
                        print 'new client: %s, %s' % (client.first_name, client.last_name)

                matter.clients.add(client)

    if cli_run:
        print 'Total imported. [cnt]%s' % total_rows
    else:
        return True, 'Total %s cases have been imported' % total_rows


def split_name(str_name):
    tokens = str_name.split(' ')
    last_name = tokens[-1].strip()
    first_name = ' '.join([t.strip() for t in tokens[:-1]])
    return first_name, last_name


if __name__ == "__main__":

    argv = sys.argv[1:]

    if len(argv) != 1 or argv[0] == '':
        print "please input file name"
        exit(1)

    _file_name = argv[0]

    msg = 'Start. [file_name]%s' % _file_name
    log(script_name=SCRIPT_NAME, level='INFO', msg=msg)

    main(_file_name)
