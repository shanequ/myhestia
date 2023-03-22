from __future__ import unicode_literals
import json
import datetime
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import Template, Context
from django.utils.html import linebreaks
from django.views.generic import TemplateView

from core.fixtures.load_matter_from_csv import main as upload_matter_csv
from matters.forms import MatterEditForm, MatterCreateForm, MatterNotificationCreateForm, \
    MatterDocUploadForm, MatterMemoUpdateForm
from matters.models import MatterRecord, MatterNotification
from my_tools.datatables import DataTableListView
from my_tools.file_parser import SimpleXLS
from my_tools.function import make_a_html, make_span_html, make_div, is_int
from my_tools.message import MyNotice
from my_tools.my_privilege import MyPrivilege
from my_tools.staff_auth import UserAuth
from my_tools.template_tag_app import matter_status_bg_class, \
    matter_property_address, matter_action_html, mn_action_html, \
    mn_status_bg_class, send_type_class, matter_client_html, matter_type_class, mn_send_to_html, make_mn_attachment_html

from myhestia.privilege_const import MATTER_VIEW
from n_template.common import NConst
from n_template.models import NTemplate


class MatterIndexView(TemplateView):

    template_name = 'matter/matter_index.html'

    def get(self, request, *args, **kwargs):

        status = request.GET.get('status', '')
        data = {
            'status': status,
            'MatterRecord': MatterRecord,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class MatterConveyingTableListView(DataTableListView):

    table_columns = [
        'pk', 'matter_num', 'matter_type', 'property_street', 'clients', 'stamp_duty_amount',
        'contract_exchange_date', 'stamp_duty_due_date', 'settlement_date', 'memo', 'matter_admin', 'status', '',
    ]

    def get_return_row(self, matter, request):

        id_html = make_a_html(href_url=reverse('matter_detail', args=[matter.pk]), text=matter.get_id_desc())
        # warning
        missed_docs = matter.get_missed_docs()
        if missed_docs:
            msg = 'Some notifications need attachments. Please upload document - <b>%s</b>. ' \
                  'Or the notification will not be sent out.' % \
                  ', '.join([t.get_type_name_display() for t in missed_docs])
            id_html += '<br><b>%s</b>' % make_span_html(text="Docs Needed ...",
                                                        css_class="txt-color-red", tooltip_title=msg)

        type_html = make_span_html(text=matter.get_matter_type_display(), css_class=matter_type_class(matter))

        address_html = make_span_html(text=matter_property_address(matter, output_type='html'),
                                      tooltip_title=matter_property_address(matter, output_type='html'))

        exchange_html = matter.contract_exchange_date.strftime('%d/%m/%Y') if matter.contract_exchange_date else ''
        exchange_html = make_div('text-center', exchange_html)

        stamp_html = matter.stamp_duty_due_date.strftime('%d/%m/%Y') if matter.stamp_duty_due_date else ''
        stamp_html = make_div('text-center', stamp_html)

        settle_html = matter.settlement_date.strftime('%d/%m/%Y') if matter.settlement_date else ''
        settle_html = make_div('text-center', settle_html)

        if UserAuth.can_edit_matter(matter=matter, request=request):
            _memo_href = reverse('matter_memo_update', args=[matter.pk])
            if matter.memo:
                memo_html = make_a_html(_memo_href, css_class='bb-dash-1',
                                        text=matter.memo, tooltip_title=matter.memo, trim_length=20)
            else:
                memo_html = make_a_html(_memo_href, text='add memo', css_class='text-muted bb-dash-1')
        else:
            memo_html = make_span_html(text=matter.memo, tooltip_title=matter.memo, trim_length=20)

        _admin_desc = matter.matter_admin.get_short_desc()
        admin_html = make_span_html(text=_admin_desc, tooltip_title=_admin_desc, trim_length=20)

        status_html = make_span_html(text=matter.get_status_display(),
                                     css_class=matter_status_bg_class(matter))

        stamp_duty_html = ''
        if matter.stamp_duty_amount is not None:
            stamp_duty_html = make_div(css_class='text-right', content='${:,.2f}'.format(matter.stamp_duty_amount))

        client_html = matter_client_html(matter, request, trim_length=30)

        action_html = matter_action_html(matter=matter, request=request)

        return_list = [
            id_html,
            matter.matter_num,
            type_html,
            address_html,
            client_html,
            stamp_duty_html,
            exchange_html,
            stamp_html,
            settle_html,
            memo_html,
            admin_html,
            status_html,
            action_html,
        ]

        return return_list

    def get_object_list(self, request, order_list):

        search_num = request.GET.get('search_num', '')
        search_client = request.GET.get('search_client', '')
        status = request.GET.get('status', '')

        result = MatterRecord.objects.filter(matter_type__in=[MatterRecord.TYPE_SALE_EXISTING,
                                                              MatterRecord.TYPE_PURCHASE_OFF_PLAN,
                                                              MatterRecord.TYPE_PURCHASE_EXISTING])

        if search_client != '':
            result = result.filter(Q(clients__en_nickname__istartswith=search_client) |
                                   Q(clients__first_name__istartswith=search_client))

        if search_num != '':
            result = result.filter(matter_num__istartswith=search_num)

        if status != '':
            result = result.filter(status=status)

        return result.distinct().order_by(*order_list).prefetch_related('clients')


class MatterOtherTableListView(DataTableListView):

    table_columns = [
        'pk', 'matter_num', 'subject', 'matter_type', 'clients', 'memo,' 'matter_admin', 'status', '',
    ]

    def get_return_row(self, matter, request):

        id_html = make_a_html(href_url=reverse('matter_detail', args=[matter.pk]), text=matter.get_id_desc())
        # warning
        missed_docs = matter.get_missed_docs()
        if missed_docs:
            msg = 'Some notifications need attachments. Please upload document - <b>%s</b>. ' \
                  'Or the notification will not be sent out.' % \
                  ', '.join([t.get_type_name_display() for t in missed_docs])
            id_html += '<br><b>%s</b>' % make_span_html(text="Docs Needed ...",
                                                        css_class="txt-color-red", tooltip_title=msg)

        type_html = make_span_html(text=matter.get_matter_type_display(), css_class=matter_type_class(matter))

        subject_html = make_span_html(text=matter.subject, tooltip_title=matter.subject, trim_length=30)

        status_html = make_span_html(text=matter.get_status_display(),
                                     css_class=matter_status_bg_class(matter))

        if UserAuth.can_edit_matter(matter=matter, request=request):
            _memo_href = reverse('matter_memo_update', args=[matter.pk])
            if matter.memo:
                memo_html = make_a_html(_memo_href, css_class='bb-dash-1',
                                        text=matter.memo, tooltip_title=matter.memo, trim_length=30)
            else:
                memo_html = make_a_html(_memo_href, text='add memo', css_class='text-muted bb-dash-1')
        else:
            memo_html = make_span_html(text=matter.memo, tooltip_title=matter.memo, trim_length=30)

        _admin_desc = matter.matter_admin.get_short_desc()
        admin_html = make_span_html(text=_admin_desc, tooltip_title=_admin_desc, trim_length=20)
        client_html = matter_client_html(matter, request, trim_length=30)

        action_html = matter_action_html(matter=matter, request=request)

        return_list = [
            id_html,
            matter.matter_num,
            subject_html,
            type_html,
            client_html,
            memo_html,
            admin_html,
            status_html,
            action_html,
        ]

        return return_list

    def get_object_list(self, request, order_list):

        search_num = request.GET.get('search_num', '')
        search_subject = request.GET.get('search_subject', '')
        search_client = request.GET.get('search_client', '')
        status = request.GET.get('status', '')

        result = MatterRecord.objects.filter(matter_type=MatterRecord.TYPE_OTHER)

        if search_client != '':
            result = result.filter(Q(clients__en_nickname__istartswith=search_client) |
                                   Q(clients__first_name__istartswith=search_client))

        if search_num != '':
            result = result.filter(matter_num__istartswith=search_num)

        if search_subject != '':
            result = result.filter(subject__icontains=search_subject)

        if status != '':
            result = result.filter(status=status)

        return result.distinct().order_by(*order_list).prefetch_related('clients')


class MatterDetailView(TemplateView):

    template_name = 'matter/matter_detail.html'

    def get(self, request, *args, **kwargs):

        matter_id = self.kwargs.get('matter_id', 0)
        matter = get_object_or_404(MatterRecord, pk=matter_id)

        data = {
            'matter': matter,
            'NConst': NConst,
            'doc_dict': matter.make_doc_file_dict(),
        }

        # a = matter.make_doc_file_dict()
        # for t, d in a.iteritems():
        #    print t, d['data']

        # warning
        missed_docs = matter.get_missed_docs()
        if missed_docs:
            msg = 'Some notifications need attachments. Please upload document - <b>%s</b>. ' \
                  'Or the notification will not be sent out.' % \
                  ', '.join([t.get_type_name_display() for t in missed_docs])
            messages.error(request, msg)

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class MatterCSVUploadView(TemplateView):

    template_name = 'matter/matter_csv_upload.html'

    def upload_csv(self, f):
        # file_name = '%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%s')
        return upload_matter_csv(f, cli_run=False)

    def post(self, request):

        errmsg = ''
        successmsg = ''
        if request.FILES:
            r, m = self.upload_csv(request.FILES['csvfile'])
            if r:
                successmsg = m
            else:
                errmsg = m
        else:
            errmsg = 'No file at all!'

        return render(request, self.template_name, {'errmsg': errmsg, 'successmsg': successmsg})


class MatterCreateView(TemplateView):

    template_name = 'matter/matter_create.html'

    def get(self, request, *args, **kwargs):

        form = MatterCreateForm(staff=request.user)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request):

        form = MatterCreateForm(data=request.POST, staff=request.user)

        data = {'form': form}

        if not form.is_valid():
            return render(request, self.template_name, data)

        matter = form.save()

        msg = "Matter(ID: %s) is created." % matter.get_id_desc()
        next_url = reverse('matter_index')

        next_action = request.POST.get("next_action", "")
        if next_action == "doc_upload":
            msg = "Matter(ID: %s) is created. Please upload documents." % matter.get_id_desc()
            next_url = reverse('matter_doc_upload', args=[matter.pk])

        messages.success(request, msg)
        return HttpResponseRedirect(next_url)


class MatterEditView(TemplateView):

    template_name = 'matter/matter_edit.html'

    def get(self, request, *args, **kwargs):

        matter_id = self.kwargs.get('matter_id', 0)
        matter = get_object_or_404(MatterRecord, pk=matter_id)

        next_url = request.GET.get("next", reverse('matter_detail', args=[matter.pk]))

        form = MatterEditForm(staff=request.user, instance=matter)

        data = {
            'form': form,
            'next': next_url,
        }

        return render(request, self.template_name, data)

    def post(self, request, matter_id):

        matter = get_object_or_404(MatterRecord, pk=matter_id)

        next_url = request.GET.get("next", reverse('matter_detail', args=[matter.pk]))

        form = MatterEditForm(staff=request.user, data=request.POST, instance=matter)

        data = {
            'form': form,
            'next': next_url,
        }

        # validate failed
        if not form.is_valid():
            return render(request, self.template_name, data)

        matter = form.save()

        messages.success(request, "Matter(ID: %s) is updated." % matter.get_id_desc())

        return HttpResponseRedirect(next_url)


class MatterDocUploadView(TemplateView):

    template_name = 'matter/matter_doc_upload.html'

    def get(self, request, *args, **kwargs):

        matter_id = self.kwargs.get('matter_id', 0)
        matter = get_object_or_404(MatterRecord, pk=matter_id)

        form = MatterDocUploadForm(staff=request.user, matter=matter)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request, matter_id):

        matter = get_object_or_404(MatterRecord, pk=matter_id)

        form = MatterDocUploadForm(staff=request.user, data=request.POST, matter=matter)

        data = {'form': form}

        # validate failed
        if not form.is_valid():
            return render(request, self.template_name, data)

        matter = form.save()

        messages.success(request, "Matter(ID: %s) document is updated." % matter.get_id_desc())

        return HttpResponseRedirect(reverse('matter_detail', args=[matter.pk]))


class MatterContractDeleteView(TemplateView):

    """
        delete (ajax post)
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, matter_id=0):
        _ = self

        if not request.is_ajax() or matter_id == 0:
            raise Http404("Page not exists")

        matter = get_object_or_404(MatterRecord, pk=matter_id)

        data = {'status': 'ok'}

        messages.success(request, "Matter contract file is deleted")

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class MatterCloseView(TemplateView):

    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, matter_id):
        _ = self

        if not request.is_ajax() or matter_id == 0:
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        matter = get_object_or_404(MatterRecord, id=matter_id)

        with transaction.atomic():
            MatterRecord.objects.filter(pk=matter_id)\
                .update(status=MatterRecord.STATUS_CLOSED, matter_close_date=datetime.date.today())

            # inactivate notification
            MatterNotification.objects.filter(matter=matter, status=MatterNotification.STATUS_WAITING)\
                .update(status=MatterNotification.STATUS_INACTIVE)

        messages.success(request, "Matter(ID: '%s') is closed. Notifications are inactivated. " % matter.get_id_desc())

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class MatterActiveView(TemplateView):

    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, matter_id):
        _ = self

        if not request.is_ajax() or matter_id == 0:
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        matter = get_object_or_404(MatterRecord, id=matter_id)

        MatterRecord.objects.filter(pk=matter_id).update(status=MatterRecord.STATUS_ACTIVE, matter_close_date=None)

        messages.success(request, "Matter(ID: %s) is activated." % matter.get_id_desc())

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class MatterDeleteView(TemplateView):
    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, matter_id):
        _ = self

        if not request.is_ajax() or matter_id == 0:
            raise Http404("Page not exists")

        next_url = request.GET.get("next", reverse('matter_index'))

        data = {
            'status': 'ok',
            'next': next_url,
        }

        matter = get_object_or_404(MatterRecord, id=matter_id)

        MatterRecord.objects.filter(pk=matter_id).delete()

        messages.success(request, "Matter(ID: %s) is deleted." % matter.get_id_desc())

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class MatterStampDutyPaidView(TemplateView):
    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, matter_id):
        _ = self

        if not request.is_ajax() or matter_id == 0:
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        today = datetime.date.today()
        matter = get_object_or_404(MatterRecord, id=matter_id)

        with transaction.atomic():
            # update matter status
            MatterRecord.objects.filter(pk=matter_id).update(status=MatterRecord.STATUS_STAMP_DUTY_PAID,
                                                             stamp_duty_paid_date=today)
            # stamp duty notifications will be inactive
            matter.mns.filter(template_trigger=NTemplate.TRIGGER_STAMP_DUTY_DUE,
                              status=MatterNotification.STATUS_WAITING)\
                .update(status=MatterNotification.STATUS_INACTIVE)

        _msg = "Matter(ID: %s) status is updated and stamp duty notifications are inactivated." % matter.get_id_desc()
        messages.success(request, _msg)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class MatterMemoUpdateView(TemplateView):

    template_name = 'matter/matter_memo_update.html'

    def get(self, request, *args, **kwargs):

        matter_id = self.kwargs.get('matter_id', 0)
        matter = get_object_or_404(MatterRecord, pk=matter_id)

        next_url = request.GET.get('next', reverse('matter_index'))

        form = MatterMemoUpdateForm(staff=request.user, instance=matter)

        data = {
            'form': form,
            'next': next_url,
        }

        return render(request, self.template_name, data)

    def post(self, request, matter_id):

        matter = get_object_or_404(MatterRecord, pk=matter_id)
        next_url = request.GET.get('next', reverse('matter_index'))

        form = MatterMemoUpdateForm(data=request.POST, staff=request.user, instance=matter)

        data = {
            'form': form,
            'next': next_url,
        }

        if not form.is_valid():
            return render(request, self.template_name, data)

        form.save()

        messages.success(request, "Memo (matterID: %s) updated." % matter.get_id_desc())

        return HttpResponseRedirect(next_url)


class MatterDownloadLeapView(TemplateView):

    def get(self, request, *args, **kwargs):

        today = datetime.date.today()
        sheet_name = 'Matter_%s' % today.strftime('%Y%m%d')

        xls_file = SimpleXLS(sheet_name=sheet_name)
        xls_file.HEADER_HEIGHT = 550
        xls_file.ROW_HEIGHT = 550

        # title
        title_list = [
            {'data': 'Matter - %s' % today.strftime('%d/%m/%Y'), 'merge': [0, 0, 0, 7]},
        ]
        xls_file.write_header(0, title_list, xls_file.data_style)

        header_list = [
            {'data': 'Matter ID'},
            {'data': 'Matter Number'},
            {'data': 'Matter Type'},
            {'data': 'Property'},
            {'data': 'Exchange Date', 'align': SimpleXLS.ALIGNMENT.HORZ_CENTER},
            {'data': 'Stamp Duty Due', 'align': SimpleXLS.ALIGNMENT.HORZ_CENTER},
            {'data': 'Stamp Duty Amount', 'align': SimpleXLS.ALIGNMENT.HORZ_RIGHT},
            {'data': 'Status'},
        ]
        xls_file.write_header(1, header_list)

        idx = 2
        query_set = MatterRecord.objects.all().order_by('-matter_num')
        for matter in query_set:
            exchange_date = matter.contract_exchange_date.strftime('%Y/%m/%d') if matter.contract_exchange_date else ''
            duty_due = matter.stamp_duty_due_date.strftime('%Y/%m/%d') if matter.stamp_duty_due_date else ''
            address = matter_property_address(matter, output_type='excel')

            _write_data = [
                {'data': matter.get_id_desc()},
                {'data': matter.matter_num},
                {'data': matter.get_matter_type_display()},
                {'data': address},
                {'data': exchange_date, 'align': SimpleXLS.ALIGNMENT.HORZ_CENTER},
                {'data': duty_due, 'align': SimpleXLS.ALIGNMENT.HORZ_CENTER},
                {'data': matter.stamp_duty_amount, 'align': SimpleXLS.ALIGNMENT.HORZ_RIGHT, 'format': SimpleXLS.FORMAT_MONEY},
                {'data': matter.get_status_display()},
            ]

            xls_file.write_row(idx, _write_data, False)
            idx += 1

        file_name = 'matter_%s.xls' % today.strftime('%Y%m%d')
        return xls_file.make_response(file_name=file_name)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class MatterNotificationIndexView(TemplateView):

    template_name = 'matter/matter_notification_index.html'

    def get(self, request, *args, **kwargs):

        status = request.GET.get('status', '')
        data = {
            'status': status,
            'MatterNotification': MatterNotification,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class MatterNotificationTableListView(DataTableListView):

    table_columns = [
        'pk', 'expect_sent_at', 'matter__matter_num', 'template_trigger', 'send_type', '',
        'content', '', 'sent_at', 'created_at', 'status', '',
    ]

    def get_return_row(self, mn, request):

        expect_sent_at_html = mn.expect_sent_at.strftime('%d/%m/%Y %H:%M') if mn.expect_sent_at else ''
        sent_at_html = mn.sent_at.strftime('%d/%m/%Y %H:%M') if mn.sent_at else ''
        created_at_html = mn.created_at.strftime('%d/%m/%Y %H:%M') if mn.created_at else ''

        matter_id_html = mn.matter.get_id_desc()
        if MyPrivilege.check_privilege(request, MATTER_VIEW):
            matter_id_html = make_a_html(href_url=reverse('matter_detail', args=[mn.matter.pk]),
                                         text=mn.matter.get_id_desc())

        id_html = mn.get_id_desc()
        # warning
        missed_docs = mn.get_missed_docs()
        if missed_docs:
            msg = 'This notification needs attachments. Please upload matter document - <b>%s</b>' % \
                  ', '.join([t.get_type_name_display() for t in missed_docs])
            id_html += '<br><b>%s</b>' % make_span_html(text="Docs Needed ...",
                                                        css_class="txt-color-red", tooltip_title=msg)

        subject = mn.subject
        if mn.send_type == NConst.SEND_TYPE_SMS:
            subject = mn.content
        content_html = make_span_html(text=subject, tooltip_title=subject, trim_length=20)

        send_to_html = mn_send_to_html(mn)

        sent_type_html = make_div(css_class="text-center %s" % send_type_class(mn.send_type),
                                  content=mn.get_send_type_display())
        attach_html = make_mn_attachment_html(mn, trim_chars=20)

        status_html = make_span_html(text=mn.get_status_display(), css_class=mn_status_bg_class(mn))

        action_html = mn_action_html(mn=mn, request=request)

        return_list = [
            id_html,
            expect_sent_at_html,
            matter_id_html,
            mn.get_trigger_desc(),
            sent_type_html,
            send_to_html,
            content_html,
            attach_html,
            sent_at_html,
            created_at_html,
            status_html,
            action_html,
        ]

        return return_list

    def get_object_list(self, request, order_list):

        search = request.GET.get('sSearch', '')
        status = request.GET.get('status', '')

        result = MatterNotification.objects

        if search != '':
            if search[0] in ['m', 'M']:
                search_id = search[1:]
                if search_id and is_int(search_id):
                    result = result.filter(matter__pk=search_id)

            elif is_int(search):
                result = result.filter(matter__pk=search)

        if status != '':
            result = result.filter(status=status)

        return result.order_by(*order_list)


class MatterNotificationDetailView(TemplateView):

    template_name = 'matter/matter_notification_detail.html'

    def get(self, request, *args, **kwargs):

        notification_id = self.kwargs.get('notification_id', 0)
        mn = get_object_or_404(MatterNotification, pk=notification_id)

        data = {
            'mn': mn,
        }

        # warning
        missed_docs = mn.get_missed_docs()
        if missed_docs:
            msg = 'This notification needs attachments. Please upload matter document. <b>%s</b>' % \
                  ', '.join([t.get_type_name_display() for t in missed_docs])
            messages.error(request, msg)

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class MatterNotificationPreviewView(TemplateView):

    def get(self, request, *args, **kwargs):

        notification_id = self.kwargs.get('notification_id', 0)
        mn = get_object_or_404(MatterNotification, pk=notification_id)

        data = MyNotice.make_matter_notification_data(mn)

        html_content = Template(mn.content).render(Context(data))

        return HttpResponse(html_content)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class MatterNotificationCreateView(TemplateView):

    template_name = 'matter/matter_notification_create.html'

    def get(self, request, *args, **kwargs):

        matter_id = self.kwargs.get('matter_id', 0)
        matter = get_object_or_404(MatterRecord, pk=matter_id)

        next_url = request.GET.get('next', reverse('matter_detail', args=[matter_id]))

        form = MatterNotificationCreateForm(staff=request.user, matter=matter)

        data = {
            'form': form,
            'next': next_url,
        }

        return render(request, self.template_name, data)

    def post(self, request, matter_id):

        matter = get_object_or_404(MatterRecord, pk=matter_id)
        next_url = request.GET.get('next', reverse('matter_detail', args=[matter_id]))

        form = MatterNotificationCreateForm(data=request.POST, staff=request.user, matter=matter)

        data = {
            'form': form,
            'next': next_url,
        }

        if not form.is_valid():
            return render(request, self.template_name, data)

        form.save()

        msg = "Notification for matter(ID: %s) is created and will be sent as soon as possible." % matter.get_id_desc()
        messages.success(request, msg)

        return HttpResponseRedirect(next_url)


class MatterNotificationInactiveView(TemplateView):

    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, notification_id):
        _ = self

        if not request.is_ajax() or notification_id == 0:
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        n = get_object_or_404(MatterNotification, id=notification_id)

        MatterNotification.objects.filter(pk=notification_id).update(status=MatterNotification.STATUS_INACTIVE)

        messages.success(request, "Notification '%s' is inactivated." % n)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class MatterNotificationActiveView(TemplateView):

    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, notification_id):
        _ = self

        if not request.is_ajax() or notification_id == 0:
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        n = get_object_or_404(MatterNotification, id=notification_id)

        MatterNotification.objects.filter(pk=notification_id).update(status=MatterNotification.STATUS_WAITING)

        messages.success(request, "Notification '%s' is activated and waiting to send." % n)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
