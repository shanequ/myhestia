from __future__ import unicode_literals

import datetime
from django.contrib.humanize.templatetags.humanize import intcomma

from my_tools.template_tag import insert_space_mobile
from my_tools.template_tag_app import matter_property_address
from django.template import Template, Context
from messaging.models import MPEmail, SMS
from myhestia import global_const
from myhestia.global_const import NOTICE_BU_NAME, EMAIL_DOMAIN, ALL_CC_EMAILS, \
    STUMP_DUTY_CHEQUE_PROVIDED_DAYS_BEFORE_DUE_DATE, EXCEPTION_MOBILE


class MyNotice(object):

    # global notice setting
    GLOBAL_DATA = {
        'OFFICIAL_URL': global_const.OFFICIAL_URL,
        'OFFICIAL_LOGO_URL': global_const.OFFICIAL_LOGO_URL,
        'NOTICE_BU_NAME': global_const.NOTICE_BU_NAME,
        'OFFICIAL_ADDRESS': global_const.OFFICIAL_ADDRESS,
        'OFFICIAL_PHONE': global_const.OFFICIAL_PHONE,
        'OFFICIAL_FAX': global_const.OFFICIAL_FAX,
    }

    @classmethod
    def render_email(cls, subject, content):
        _wrapper = '{%% extends "emailbase.html" %%}' \
                   '{%% block title %%} %s {{ block.super }}{%% endblock %%}' \
                   '{%% block content %%}%s{%% endblock %%}' % (subject, content,)
        return _wrapper

    @classmethod
    def make_matter_notification_data(cls, mn=None):
        """
        Make data to generate matter / preview notification

        Args:
            mn: MatterNotification or None if template

        Return:
            {}
        """
        # merge global setting
        ret_dict = cls.GLOBAL_DATA

        matter_number = "{{ matter_number }}"
        client_name = "{{ client_name }}"
        property_address = "{{ property_address }}"
        exchange_date = "{{ exchange_date }}"
        cooling_off_date = "{{ cooling_off_date }}"
        stamp_duty_due_date = "{{ stamp_duty_due_date }}"
        stamp_duty_cheque_provided_date = "{{ stamp_duty_cheque_provided_date }}"
        settlement_date = "{{ settlement_date }}"
        stamp_duty_amount = "{{ stamp_duty_amount }}"
        agent_name = "{{ agent_name }}"
        agent_email = "{{ agent_email }}"
        agent_mobile = "{{ agent_mobile }}"
        admin = "{{ admin }}"
        admin_email = "{{ admin_email }}"
        admin_mobile = "{{ admin_mobile }}"
        solicitor = "{{ solicitor }}"
        solicitor_email = "{{ solicitor_email }}"
        solicitor_mobile = "{{ solicitor_mobile }}"

        if mn:
            matter = mn.matter

            matter_number = matter.matter_num
            client_name = ', '.join([c.get_legal_name() for c in matter.clients.all()])
            property_address = matter_property_address(matter, output_type='text')

            # 1 January 2017
            exchange_date = matter.contract_exchange_date.strftime('%d %B %Y') if matter.contract_exchange_date else ''
            cooling_off_date = matter.cooling_off_date.strftime('%d %B %Y') if matter.cooling_off_date else ''
            stamp_duty_due_date = matter.stamp_duty_due_date.strftime('%d %B %Y') if matter.stamp_duty_due_date else ''
            stamp_duty_cheque_provided_date = ''
            if matter.stamp_duty_due_date:
                _cheque_provided_date = matter.stamp_duty_due_date - datetime.timedelta(STUMP_DUTY_CHEQUE_PROVIDED_DAYS_BEFORE_DUE_DATE)
                stamp_duty_cheque_provided_date = _cheque_provided_date.strftime('%d %B %Y')

            settlement_date = matter.settlement_date.strftime('%d %B %Y') if matter.settlement_date else ''

            stamp_duty_amount = '$' + intcomma(matter.stamp_duty_amount) if matter.stamp_duty_amount is not None else ''

            if matter.agent_contact and matter.agent_contact.agent:
                _agent = matter.agent_contact.agent
                agent_name = _agent.agent_name
                agent_email = matter.agent_contact.contact_email
                agent_mobile = insert_space_mobile(matter.agent_contact.contact_mobile)

            admin = matter.matter_admin.get_full_en_name()
            admin_email = matter.matter_admin.email
            admin_mobile = matter.matter_admin.mobile

            solicitor = matter.solicitor_name
            solicitor_email = matter.solicitor_email
            solicitor_mobile = matter.solicitor_mobile

        ret_dict.update({
            'matter_number': matter_number,
            'client_name': client_name,
            'property_address': property_address,

            # agent
            'agent_name': agent_name,
            'agent_email': agent_email,
            'agent_mobile': agent_mobile,

            # 1 January 2017
            'exchange_date': exchange_date,
            'cooling_off_date': cooling_off_date,
            'stamp_duty_due_date': stamp_duty_due_date,
            'stamp_duty_cheque_provided_date': stamp_duty_cheque_provided_date,
            'settlement_date': settlement_date,

            'stamp_duty_amount': stamp_duty_amount,

            # person responsible
            'admin': admin,
            'admin_email': admin_email,
            'admin_mobile': admin_mobile,

            'solicitor': solicitor,
            'solicitor_email': solicitor_email,
            'solicitor_mobile': solicitor_mobile,
        })

        return ret_dict

    @classmethod
    def _make_template_data(cls, **kwargs):
        """
        Initial template data

        Args:
            kwargs:

        Return:
             data dict
        """
        if 'mn' not in kwargs:
            return cls.GLOBAL_DATA.update(kwargs)

        mn = kwargs['mn']
        return cls.make_matter_notification_data(mn=mn)

    @classmethod
    def send_sms(cls, mobiles, sms_text='', **kwargs):
        """
        URL:
        Method: POST
        Parameters:

            to   [ a list of mobile numbers, comma-separated] compulsory
            from  [ any text] optional, max. 30
            text  [the test message, max. 250 chars] compulsory


        Return:

        """
        if not mobiles or not sms_text:
            return

        send_from = NOTICE_BU_NAME

        tos = []
        for mobile in mobiles:
            if mobile in ['', None, EXCEPTION_MOBILE]:
                continue
            tos.append(mobile)

        send_to = ','.join(tos)

        if not send_to:
            return

        template_data = cls._make_template_data(**kwargs)
        html_content = Template(sms_text).render(Context(template_data))

        data_dict = {
            'target_numbers': send_to,
            'sms_text': html_content,
            'sms_from': send_from
        }

        sms = SMS(**data_dict)
        sms.save()

        return sms

    @classmethod
    def send_email(cls, to_emails, subject, template='', cc_emails=None, attach_global_files=None, **kwargs):
        """
            Common function to put the email to the Queue
        """
        if not to_emails or not subject or not template:
            return None

        to_email_str = ','.join(to_emails) if to_emails else ''
        cc_email_str = ','.join(cc_emails) if cc_emails else ''
        attachment_str = ','.join([gf.file.name for gf in attach_global_files]) if attach_global_files else ''

        template_data = cls._make_template_data(**kwargs)

        html_subject = Template(subject).render(Context(template_data))
        html_content = Template(template).render(Context(template_data))

        data_dict = {
            'status': 'P',
            'no_reply': False,
            'from_email_desc': NOTICE_BU_NAME,
            'from_email': '',

            'to_email': to_email_str,
            'cc_email': cc_email_str,
            'subject': html_subject[:128],
            'text_content': '',
            'html_content': html_content,
            'attach_file_list': attachment_str,
        }

        mp_email = MPEmail(**data_dict)
        mp_email.save()

        return mp_email
