from __future__ import unicode_literals
from django import forms
from django.db import transaction
from django.db.models import Q
from django.forms import ModelForm
from agent.models import AgentContact, Agent


class AgentContactCreateForm(ModelForm):

    agent_name = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        super(AgentContactCreateForm, self).__init__(*args, **kwargs)

        self.agent_list = [a.agent_name for a in Agent.objects.order_by('agent_name')]

    def clean_agent_name(self):
        return self.cleaned_data.get('agent_name').strip()

    def clean_contact_email(self):
        return self.cleaned_data.get('contact_email').strip().replace(' ', '')

    def clean_contact_mobile(self):
        return self.cleaned_data.get('contact_mobile').strip().replace(' ', '')

    def clean(self):
        agent_name = self.cleaned_data.get('agent_name', '')
        contact_name = self.cleaned_data.get('contact_name', '')
        contact_email = self.cleaned_data.get('contact_email', '')
        contact_mobile = self.cleaned_data.get('contact_mobile', '')

        if AgentContact.objects.filter(
                Q(agent__agent_name=agent_name) &
                Q(contact_name=contact_name) & (
                    Q(contact_email=contact_email) | Q(contact_mobile=contact_mobile)
                )).exists():
            raise forms.ValidationError('Agent contact (%s) has already existed.' % contact_name)

        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        agent_name = self.cleaned_data.get('agent_name')

        with transaction.atomic():
            agent = Agent.objects.filter(agent_name=agent_name).first()
            if not agent:
                agent = Agent()
                agent.agent_name = agent_name
                agent.save()

            contact = super(AgentContactCreateForm, self).save(commit=False)
            contact.agent = agent
            contact.save()

        return contact

    class Meta:
        model = AgentContact
        fields = [
            'contact_name', 'contact_email', 'contact_mobile',
        ]


class AgentContactEditForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        super(AgentContactEditForm, self).__init__(*args, **kwargs)

        self.agent_list = [a.agent_name for a in Agent.objects.order_by('agent_name')]

    def clean_agent_name(self):
        return self.cleaned_data.get('agent_name').strip()

    def clean_contact_email(self):
        return self.cleaned_data.get('contact_email').strip().replace(' ', '')

    def clean_contact_mobile(self):
        return self.cleaned_data.get('contact_mobile').strip().replace(' ', '')

    def clean(self):
        agent = self.instance.agent
        contact_name = self.cleaned_data.get('contact_name', '').strip()
        contact_email = self.cleaned_data.get('contact_email', '').strip()
        contact_mobile = self.cleaned_data.get('contact_mobile', '').strip()

        if AgentContact.objects.filter(
                Q(agent__pk=agent.pk) & ~Q(pk=self.instance.pk) &
                Q(contact_name=contact_name) & (
                    Q(contact_email=contact_email) | Q(contact_mobile=contact_mobile)
                )).exists():
            raise forms.ValidationError('Agent contact (%s) has already existed.' % contact_name)

        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        with transaction.atomic():
            contact = super(AgentContactEditForm, self).save(commit=False)
            contact.save()

        return contact

    class Meta:
        model = AgentContact
        fields = [
            'contact_name', 'contact_email', 'contact_mobile',
        ]
