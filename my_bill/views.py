from __future__ import unicode_literals
import datetime
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView
from matters.models import MatterRecord
from messaging.models import SMS, MPEmail
from my_tools.datatables import DataTableListView
from my_tools.function import make_a_html, make_span_html, make_div, get_period_range
from my_tools.staff_auth import UserAuth
from my_tools.template_tag_app import matter_status_bg_class, \
    matter_property_address, matter_action_html, matter_client_html, matter_type_class


class BillIndexView(TemplateView):

    template_name = 'my_bill/sms_email_history_index.html'

    def get(self, request, *args, **kwargs):

        today = datetime.date.today()
        date_start, date_end = get_period_range(today, period_type='month')

        data = {
            'date_start': date_start.strftime('%d-%m-%Y'),
            'date_end': date_end.strftime('%d-%m-%Y'),
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class BillIndexSMSTableListView(DataTableListView):

    table_columns = [
        'pk', 'insert_time', '', 'sms_text', 'target_numbers',
    ]

    def get_return_row(self, sms, request):

        id_html = sms.pk

        insert_time_html = sms.insert_time.strftime('%d/%m/%Y %H:%M:%S') if sms.insert_time else ''

        target_numbers = sms.target_numbers.split(',')
        sms_cnt_html = make_div(css_class='text-center', content=len(target_numbers))
        sms_text_html = make_span_html(text=sms.sms_text, tooltip_title=sms.sms_text, trim_length=80)
        target_numbers_html = '<br>'.join(target_numbers)

        return_list = [
            id_html,
            insert_time_html,
            sms_cnt_html,
            sms_text_html,
            target_numbers_html,
        ]

        return return_list

    def get_object_list(self, request, order_list):

        try:
            start_date_str = request.GET.get('sms_start_date', '')
            start_date = datetime.datetime.strptime(start_date_str, "%d-%m-%Y")

        except ValueError:
            start_date = None

        try:
            end_date_str = request.GET.get('sms_end_date', '')
            end_date = datetime.datetime.strptime(end_date_str, "%d-%m-%Y")

        except ValueError:
            end_date = None

        if end_date:
            end_date = datetime.datetime.combine(end_date, datetime.time(23, 59, 59))

        result = SMS.objects.filter(status=SMS.STATUS_SENT)

        if start_date:
            result = result.filter(insert_time__gte=start_date)

        if end_date:
            result = result.filter(insert_time__lte=end_date)

        total_cnt = 0
        for sms in result:
            total_cnt += len(sms.target_numbers.split(','))

        self.callback_data = {'total_sms': total_cnt}

        return result.order_by(*order_list)


class BillIndexEmailTableListView(DataTableListView):

    table_columns = [
        'pk', 'sent_out_time', 'subject', 'to_email', 'cc_email', 'attach_file_list',
    ]

    def get_return_row(self, email, request):

        id_html = email.pk
        sent_out_time_html = email.sent_out_time.strftime('%d/%m/%Y %H:%M:%S') if email.sent_out_time else ''
        subject_html = make_span_html(text=email.subject, tooltip_title=email.subject, trim_length=60)
        to_email_html = make_span_html(text=email.to_email, tooltip_title=email.to_email, trim_length=30)
        cc_email_html = make_span_html(text=email.cc_email, tooltip_title=email.cc_email, trim_length=30)
        attachment_html = 'Yes' if email.attach_file_list else 'No'
        attachment_html = make_div(css_class='text-center', content=attachment_html)

        return_list = [
            id_html,
            sent_out_time_html,
            subject_html,
            to_email_html,
            cc_email_html,
            attachment_html,
        ]

        return return_list

    def get_object_list(self, request, order_list):

        try:
            start_date_str = request.GET.get('email_start_date', '')
            start_date = datetime.datetime.strptime(start_date_str, "%d-%m-%Y")

        except ValueError:
            start_date = None

        try:
            end_date_str = request.GET.get('email_end_date', '')
            end_date = datetime.datetime.strptime(end_date_str, "%d-%m-%Y")

        except ValueError:
            end_date = None

        if end_date:
            end_date = datetime.datetime.combine(end_date, datetime.time(23, 59, 59))

        result = MPEmail.objects.filter(status=MPEmail.STATUS_SENT)

        if start_date:
            result = result.filter(sent_out_time__gte=start_date)

        if end_date:
            result = result.filter(sent_out_time__lte=end_date)

        total_cnt = result.count()
        self.callback_data = {'total_email': total_cnt}

        return result.order_by(*order_list)

