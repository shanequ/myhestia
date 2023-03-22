from __future__ import unicode_literals

import datetime
from django.http import Http404
from django.views.generic import TemplateView

from matters.models import MatterNotification
from my_tools.file_parser import SimpleXLS
from my_tools.template_tag_app import matter_property_address, matter_client_desc
from n_template.common import NConst
from n_template.models import NTemplate


class ReportStampDutyNotificationDownloadView(TemplateView):

    def get(self, request, *args, **kwargs):

        today = datetime.date.today()
        one_month = today + datetime.timedelta(32)

        query_set = MatterNotification.objects.filter(matter__stamp_duty_due_date__range=[today, one_month],
                                                      template_trigger=NTemplate.TRIGGER_STAMP_DUTY_DUE,
                                                      status__in=[MatterNotification.STATUS_WAITING]).order_by('-matter__stamp_duty_due_date')

        _today = datetime.date.today()
        _sheet_name = 'Stamp_Duty_%s' % _today.strftime('%Y%m%d')
        xls_file = SimpleXLS(sheet_name=_sheet_name)
        xls_file.HEADER_HEIGHT = 550
        xls_file.ROW_HEIGHT = 550

        # title
        title_list = [
            {'data': 'Stamp Duty Notification In One Month - %s' % _today.strftime('%d/%m/%Y'), 'merge': [0, 0, 0, 12]},
        ]
        xls_file.write_header(0, title_list, xls_file.data_style)

        header_list = [
            {'data': 'ID'},
            {'data': 'Expected Sent At'},
            {'data': 'Trigger'},
            {'data': 'Matter ID'},
            {'data': 'Matter Type'},
            {'data': 'Property'},
            {'data': 'Client'},
            {'data': 'Stamp Duty Due', 'align': SimpleXLS.ALIGNMENT.HORZ_CENTER},
            {'data': 'Stamp Duty Amount', 'align': SimpleXLS.ALIGNMENT.HORZ_RIGHT},
            {'data': 'Send Type', 'align': SimpleXLS.ALIGNMENT.HORZ_CENTER},
            {'data': 'Sent To'},
            {'data': 'CC To'},
            {'data': 'Status'},
        ]
        xls_file.write_header(1, header_list)

        idx = 2
        for mn in query_set:
            _matter = mn.matter
            expect_sent_at = mn.expect_sent_at.strftime('%d/%m/%Y %H:%M') if mn.expect_sent_at else ''
            duty_due = _matter.stamp_duty_due_date.strftime('%d/%m/%Y') if _matter.stamp_duty_due_date else ''
            address = matter_property_address(_matter, output_type='excel')
            client = matter_client_desc(_matter, separator='\n')

            send_to = ', '.join([r.get_receiver_display() for r in mn.send_tos.all()])
            cc_to = ', '.join([r.get_receiver_display() for r in mn.cc_tos.all()])

            _write_data = [
                {'data': mn.get_id_desc()},
                {'data': expect_sent_at},
                {'data': mn.get_trigger_desc()},
                {'data': _matter.get_id_desc()},
                {'data': _matter.get_matter_type_display()},
                {'data': address},
                {'data': client},
                {'data': duty_due, 'align': SimpleXLS.ALIGNMENT.HORZ_CENTER},
                {'data': _matter.stamp_duty_amount, 'align': SimpleXLS.ALIGNMENT.HORZ_RIGHT, 'format': SimpleXLS.FORMAT_MONEY},
                {'data': mn.get_send_type_display(), 'align': SimpleXLS.ALIGNMENT.HORZ_CENTER},
                {'data': send_to},
                {'data': cc_to},
                {'data': mn.get_status_display()},
            ]

            xls_file.write_row(idx, _write_data, False)
            idx += 1

        file_name = 'stump_duty_notification_%s.xls' % datetime.date.today().strftime('%Y%m%d')
        return xls_file.make_response(file_name=file_name)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


def make_commission_report_my_data(sales_id, project_title='', exchange_date_from=None, exchange_date_to=None):
    """
    Make my commission report data

    Args:
        sales_id            - auth_user pk
        project_title       - project title or ''
        exchange_date_from  - date or None
        exchange_date_to    - date or None

    Returns:
        query, data - {
            'paid_sc_amount': _total_paid_sc,
            'paid_tlf_amount': _total_paid_tlf,
            'pending_sc_amount': _total_pending_sc,
            'pending_tlf_amount': _total_pending_tlf,
            'forecast_sc_amount': _total_forecast_sc,
            'forecast_tlf_amount': _total_forecast_tlf,
            'total_amount': _total,
        }
    """
    result = SalesCommission.objects.filter(payee__pk=sales_id,
                                            status__in=[SalesCommission.STATUS_CONFIRMING,
                                                        SalesCommission.STATUS_APPROVING,
                                                        SalesCommission.STATUS_PAYING,
                                                        SalesCommission.STATUS_PAID])

    if exchange_date_from:
        exchange_at_from = datetime.datetime.combine(exchange_date_from, datetime.datetime.min.time())
        result = result.filter(sales_record__contract_exchanged_at__gte=exchange_at_from)

    if exchange_date_to:
        exchange_at_to = datetime.datetime.combine(exchange_date_to, datetime.datetime.max.time())
        result = result.filter(sales_record__contract_exchanged_at__lte=exchange_at_to)

    if project_title != '':
        result = result.filter(sales_record__sales_project__title__icontains=project_title)

    #
    # calc pending, paid, total commission amount
    #
    _total_paid_sc = decimal.Decimal(0)
    _total_paid_tlf = decimal.Decimal(0)
    _total_pending_sc = decimal.Decimal(0)
    _total_pending_tlf = decimal.Decimal(0)
    _total_forecast_sc = decimal.Decimal(0)
    _total_forecast_tlf = decimal.Decimal(0)
    _total = decimal.Decimal(0)

    _stats = result.values('status', 'instalment', 'sc_type').annotate(amount=Sum('amount'))

    for _stat in _stats:
        _instalment = _stat['instalment']
        _sc_type = _stat['sc_type']
        _status = _stat['status']
        _amount = _stat['amount']

        if _status == SalesCommission.STATUS_PAID and \
                _sc_type == SalesCommission.SC_TYPE_SALES:
            _total_paid_sc += _amount

        elif _status == SalesCommission.STATUS_PAID and \
                _sc_type in [SalesCommission.SC_TYPE_MTR, SalesCommission.SC_TYPE_PTR]:
            _total_paid_tlf += _amount

        elif _status != SalesCommission.STATUS_PAID and \
                _sc_type == SalesCommission.SC_TYPE_SALES and \
                _instalment in [SalesCommission.INSTALMENT_1, SalesCommission.INSTALMENT_FINAL]:
            _total_pending_sc += _amount

        elif _status != SalesCommission.STATUS_PAID and \
                _sc_type in [SalesCommission.SC_TYPE_MTR, SalesCommission.SC_TYPE_PTR] and \
                _instalment in [SalesCommission.INSTALMENT_1, SalesCommission.INSTALMENT_FINAL]:
            _total_pending_tlf += _amount

        elif _status != SalesCommission.STATUS_PAID and \
                _sc_type == SalesCommission.SC_TYPE_SALES and \
                _instalment == SalesCommission.INSTALMENT_FC_FINAL:
            _total_forecast_sc += _amount

        elif _status != SalesCommission.STATUS_PAID and \
                _sc_type in [SalesCommission.SC_TYPE_MTR, SalesCommission.SC_TYPE_PTR] and \
                _instalment == SalesCommission.INSTALMENT_FC_FINAL:
            _total_forecast_tlf += _amount

        _total += _amount

    sum_data = {
        'paid_sc_amount': _total_paid_sc,
        'paid_tlf_amount': _total_paid_tlf,
        'pending_sc_amount': _total_pending_sc,
        'pending_tlf_amount': _total_pending_tlf,
        'forecast_sc_amount': _total_forecast_sc,
        'forecast_tlf_amount': _total_forecast_tlf,
        'total_amount': _total,
    }

    query_set = result.select_related('sales_record__sales_project', 'sales_record__property_for_sale', 'payee')

    return query_set, sum_data
