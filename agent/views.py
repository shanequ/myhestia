from __future__ import unicode_literals
import json
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from agent.forms import AgentContactCreateForm, AgentContactEditForm
from agent.models import AgentContact, Agent
from my_tools.datatables import DataTableListView
from my_tools.function import make_a_html, make_span_html
from my_tools.template_tag_app import agent_contact_action_html
from n_template.common import NConst


class AgentDetailView(TemplateView):

    template_name = 'agent/agent_detail.html'

    def get(self, request, *args, **kwargs):

        agent_id = self.kwargs.get('agent_id', 0)
        agent = get_object_or_404(Agent, pk=agent_id)

        data = {
            'agent': agent,
            'NConst': NConst,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class AgentContactIndexView(TemplateView):

    template_name = 'agent/agent_contact_index.html'

    def get(self, request, *args, **kwargs):
        data = {}
        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class AgentContactTableListView(DataTableListView):

    table_columns = [
        'pk', 'agent__agent_name', 'contact_name', 'contact_email', 'contact_mobile', '',
    ]

    def get_return_row(self, contact, request):

        id_html = contact.pk

        agent_html = make_a_html(href_url=reverse('agent_detail', args=[contact.agent.pk]),
                                 text=contact.agent.agent_name, tooltip_title=contact.agent.agent_name, trim_length=40)

        contact_html = make_span_html(text=contact.contact_name, tooltip_title=contact.contact_name, trim_length=30)

        email_html = make_span_html(text=contact.contact_email, tooltip_title=contact.contact_email, trim_length=30)

        mobile_html = contact.contact_mobile

        action_html = agent_contact_action_html(contact=contact, request=request)

        return_list = [
            id_html,
            agent_html,
            contact_html,
            email_html,
            mobile_html,
            action_html,
        ]

        return return_list

    def get_object_list(self, request, order_list):

        search_name = request.GET.get('sSearch', '')

        result = AgentContact.objects

        if search_name != '':
            result = result.filter(Q(contact_name__istartswith=search_name) |
                                   Q(agent__agent_name__istartswith=search_name))

        return result.order_by(*order_list).select_related('agent')


class AgentContactCreateView(TemplateView):

    template_name = 'agent/agent_contact_create.html'

    def get(self, request, *args, **kwargs):

        form = AgentContactCreateForm(staff=request.user)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request):

        form = AgentContactCreateForm(data=request.POST, staff=request.user)

        data = {'form': form}

        if not form.is_valid():
            return render(request, self.template_name, data)

        contact = form.save()

        msg = "Agent contact (%s) is created." % contact.contact_name
        messages.success(request, msg)

        return HttpResponseRedirect(reverse('agent_contact_index'))


class AgentContactCreateModalView(TemplateView):

    template_name = 'agent/_agent_contact_create_modal.html'

    def get(self, request, *args, **kwargs):

        form = AgentContactCreateForm(staff=request.user)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self

        if not request.is_ajax():
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        form = AgentContactCreateForm(data=request.POST, staff=request.user)
        if not form.is_valid():
            data['status'] = 'error'
            data['message'] = '<br>'.join(["%s: %s" % (k if k != '__all__' else 'Error', v.as_text(),)
                                           for k, v in form.errors.items()])
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

        contact = form.save()

        data['id'] = contact.pk
        data['text'] = str(contact)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class AgentContactEditView(TemplateView):

    template_name = 'agent/agent_contact_edit.html'

    def get(self, request, *args, **kwargs):

        contact_id = self.kwargs.get('contact_id', 0)
        contact = get_object_or_404(AgentContact, pk=contact_id)

        next_url = request.GET.get("next", reverse('agent_contact_index'))

        form = AgentContactEditForm(staff=request.user, instance=contact)

        data = {
            'form': form,
            'next': next_url,
        }

        return render(request, self.template_name, data)

    def post(self, request, contact_id):

        contact = get_object_or_404(AgentContact, pk=contact_id)

        next_url = request.GET.get("next", reverse('agent_contact_index'))

        form = AgentContactEditForm(staff=request.user, data=request.POST, instance=contact)

        data = {
            'form': form,
            'next': next_url,
        }

        # validate failed
        if not form.is_valid():
            return render(request, self.template_name, data)

        contact = form.save()

        msg = "Agent contact (%s) is updated." % contact.contact_name
        messages.success(request, msg)

        return HttpResponseRedirect(next_url)


class AgentContactDeleteView(TemplateView):

    """
        delete (ajax post)
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, contact_id=0):
        _ = self

        if not request.is_ajax() or contact_id == 0:
            raise Http404("Page not exists")

        next_url = request.GET.get("next", reverse('agent_contact_index'))

        contact = get_object_or_404(AgentContact, pk=contact_id)

        data = {
            'status': 'ok',
            'next': next_url,
        }

        # check
        if contact.agent_contact_matters.exists():
            data['status'] = 'error'
            data['message'] = 'Can NOT delete this contact. Some matter is using it.'
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

        AgentContact.objects.filter(pk=contact_id).delete()

        messages.success(request, "Agent contact (%s) is deleted." % contact.contact_name)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
