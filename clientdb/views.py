from __future__ import unicode_literals
import json
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.html import linebreaks
from django.views.generic import TemplateView
from clientdb.forms import ClientCreateForm, ClientEditForm, ClientMemoChangeForm
from clientdb.models import Client
from my_tools.datatables import DataTableListView
from my_tools.function import make_a_html, make_span_html, make_div
from my_tools.staff_auth import UserAuth
from my_tools.template_tag import get_gender_class, insert_space, insert_space_mobile
from my_tools.template_tag_app import client_status_bg_class, client_action_html
from n_template.common import NConst


class ClientIndexView(TemplateView):

    template_name = 'client/client_index.html'

    def get(self, request, *args, **kwargs):

        status = request.GET.get('status', '')
        data = {
            'status': status,
            'Client': Client,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class ClientTableListView(DataTableListView):

    table_columns = [
        'pk', 'first_name', 'email', 'mobile', 'dob', 'gender', 'memo', 'status', '',
    ]

    def get_return_row(self, client, request):

        name_html = make_a_html(href_url=reverse('client_detail', args=[client.pk]),
                                tooltip_title=client, trim_length=30, text=client.get_name_desc())

        email_html = make_a_html(href_url="mailto: %s" % client.email, text=client.email, tooltip_title=client.email, trim_length=30)
        dob_html = client.dob.strftime('%d/%m/%Y') if client.dob else ''
        gender_html = make_div(content=client.get_gender_display(),
                               css_class="text-center %s" % get_gender_class(client.gender))

        status_html = make_span_html(text=client.get_status_display(),
                                     css_class=client_status_bg_class(client))

        if UserAuth.can_change_client_memo(client=client, request=request):
            _memo_href = reverse('client_memo_change', args=[client.pk])
            if client.memo:
                memo_html = make_a_html(_memo_href, css_class='bb-dash-1',
                                        text=client.memo, tooltip_title=client.memo, trim_length=30)
            else:
                memo_html = make_a_html(_memo_href, text='add memo', css_class='text-muted bb-dash-1')
        else:
            memo_html = make_span_html(text=client.memo, tooltip_title=client.memo, trim_length=30)

        action_html = client_action_html(client=client, request=request)

        return_list = [
            client.pk,
            name_html,
            email_html,
            insert_space_mobile(client.mobile),
            dob_html,
            gender_html,
            memo_html,
            status_html,
            action_html,
        ]

        return return_list

    def get_object_list(self, request, order_list):

        search = request.GET.get('sSearch', '')
        status = request.GET.get('status', '')

        result = Client.objects

        if search != '':
            result = result.filter(Q(en_nickname__istartswith=search) | Q(first_name__istartswith=search))

        if status != '':
            result = result.filter(status=status)

        return result.order_by(*order_list)


class ClientDetailView(TemplateView):

    template_name = 'client/client_detail.html'

    def get(self, request, *args, **kwargs):

        client_id = self.kwargs.get('client_id', 0)
        client = get_object_or_404(Client, pk=client_id)

        data = {
            'client': client,
            'NConst': NConst,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class ClientCreateView(TemplateView):

    template_name = 'client/client_create.html'

    def get(self, request, *args, **kwargs):

        form = ClientCreateForm(staff=request.user)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request):

        form = ClientCreateForm(data=request.POST, staff=request.user)

        data = {'form': form}

        if not form.is_valid():
            return render(request, self.template_name, data)

        client = form.save()

        msg = "Client '%s' is created." % client.get_short_desc()
        messages.success(request, msg)

        return HttpResponseRedirect(reverse('client_index'))


class ClientCreateModalView(TemplateView):

    template_name = 'client/_client_create_modal.html'

    def get(self, request, *args, **kwargs):

        form = ClientCreateForm(staff=request.user)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self

        if not request.is_ajax():
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        form = ClientCreateForm(data=request.POST, staff=request.user)
        if not form.is_valid():
            data['status'] = 'error'
            data['message'] = '<br>'.join(["%s: %s" % (k if k != '__all__' else 'Error', v.as_text(),)
                                           for k, v in form.errors.items()])
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

        client = form.save()

        data['id'] = client.pk
        data['text'] = str(client)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class ClientEditView(TemplateView):

    template_name = 'client/client_edit.html'

    def get(self, request, *args, **kwargs):

        client_id = self.kwargs.get('client_id', 0)
        client = get_object_or_404(Client, pk=client_id)

        next_url = request.GET.get('next', reverse('client_detail', args=[client.pk]))

        form = ClientEditForm(staff=request.user, instance=client)

        data = {
            'form': form,
            'next': next_url,
        }

        return render(request, self.template_name, data)

    def post(self, request, client_id):

        client = get_object_or_404(Client, pk=client_id)

        next_url = request.GET.get('next', reverse('client_detail', args=[client.pk]))

        form = ClientEditForm(staff=request.user, data=request.POST, instance=client)

        data = {
            'form': form,
            'next': next_url,
        }

        # validate failed
        if not form.is_valid():
            return render(request, self.template_name, data)

        client = form.save()

        messages.success(request, "Client '%s' is updated" % client.get_short_desc())

        return HttpResponseRedirect(next_url)


class ClientInactiveView(TemplateView):

    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, client_id):
        _ = self

        if not request.is_ajax() or client_id == 0:
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        client = get_object_or_404(Client, id=client_id)

        Client.objects.filter(pk=client_id).update(status=Client.STATUS_INACTIVE)

        messages.success(request, "Client '%s' is inactivated." % client.get_short_desc())

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class ClientActiveView(TemplateView):

    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, client_id):
        _ = self

        if not request.is_ajax() or client_id == 0:
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        client = get_object_or_404(Client, id=client_id)

        Client.objects.filter(pk=client_id).update(status=Client.STATUS_ACTIVE)

        messages.success(request, "Client '%s' is activated." % client.get_short_desc())

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class ClientDeleteView(TemplateView):
    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, client_id):
        _ = self

        if not request.is_ajax() or client_id == 0:
            raise Http404("Page not exists")

        next_url = request.GET.get("next", reverse('client_index'))

        data = {
            'status': 'ok',
            'next': next_url,
        }

        client = get_object_or_404(Client, id=client_id)

        # check
        if client.client_matters.exists():
            data['status'] = 'error'
            data['message'] = 'Can NOT delete this client. Some matter is using it.'
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

        Client.objects.filter(pk=client_id).delete()

        messages.success(request, "Client '%s' is deleted." % client.get_short_desc())

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class ClientMemoChangeView(TemplateView):

    template_name = 'client/client_memo_change.html'

    def get(self, request, *args, **kwargs):

        client_id = self.kwargs.get('client_id', 0)
        client = get_object_or_404(Client, pk=client_id)

        next_url = request.GET.get('next', reverse('client_index'))

        form = ClientMemoChangeForm(staff=request.user, instance=client)

        data = {
            'form': form,
            'next': next_url,
        }

        return render(request, self.template_name, data)

    def post(self, request, client_id):

        client = get_object_or_404(Client, pk=client_id)

        next_url = request.GET.get('next', reverse('client_index'))

        form = ClientMemoChangeForm(data=request.POST, staff=request.user, instance=client)

        data = {
            'form': form,
            'next': next_url,
        }

        if not form.is_valid():
            return render(request, self.template_name, data)

        form.save()

        messages.success(request, "Memo updated (%s)." % client.get_short_desc())

        return HttpResponseRedirect(next_url)
