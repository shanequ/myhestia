from __future__ import unicode_literals
import datetime
from django import forms
from django.db import transaction
from django.db.models import Q
from django.forms import ModelForm
from agent.models import AgentContact
from clientdb.models import Client
from core.commons import CommonConst
from core.models import GlobalFile, Staff
from matters.common import update_matter_notifications
from matters.models import MatterRecord, MatterNotification, MatterDocument
from my_tools.message import MyNotice
from n_template.common import NConst
from n_template.models import NTemplate, NReceiver, AttachmentType
from project.models import Project


class MatterCreateForm(ModelForm):

    clients = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        self.MatterRecord = MatterRecord
        self.CommonConst = CommonConst
        super(MatterCreateForm, self).__init__(*args, **kwargs)

        self.fields['clients'].queryset = Client.objects.filter(status=Client.STATUS_ACTIVE).order_by('en_nickname')
        self.matter_admins = Staff.objects.filter(
            Q(status=Staff.STATUS_ACTIVE) & ~Q(user_type=Staff.USER_TYPE_SYSADMIN)
        ).order_by('-created_at')

        self.agent_contact_choices = AgentContact.objects.order_by('contact_name')
        self.project_choices = Project.objects.order_by('title')

    def clean_matter_num(self):
        matter_num = self.cleaned_data.get('matter_num', '').strip()
        return matter_num

    def clean(self):
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        clients = self.cleaned_data.get('clients', [])

        with transaction.atomic():
            matter = super(MatterCreateForm, self).save(commit=False)
            matter.created_by = self.staff
            matter.save()

            # add client
            matter.clients.add(*clients)

            if matter.matter_type != MatterRecord.TYPE_OTHER:
                update_matter_notifications(new_matter=matter, old_matter=None)

        return matter

    class Meta:
        model = MatterRecord
        fields = [
            'matter_num', 'matter_type', 'matter_admin', 'subject', 'project',
            'property_street', 'property_suburb', 'property_postcode', 'property_state', 'agent_contact',
            'stamp_duty_amount', 'stamp_duty_due_date', 'stamp_duty_paid_date',
            'contract_exchange_date', 'cooling_off_date', 'settlement_date',
            'solicitor_name', 'solicitor_email', 'solicitor_mobile',
        ]


class MatterEditForm(ModelForm):

    clients = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        self.MatterRecord = MatterRecord
        self.CommonConst = CommonConst
        super(MatterEditForm, self).__init__(*args, **kwargs)

        self.fields['clients'].queryset = Client.objects.filter(status=Client.STATUS_ACTIVE).order_by('en_nickname')
        self.fields['clients'].initial = [str(c.pk) for c in self.instance.clients.all()]

        self.matter_admins = Staff.objects.filter(
            Q(status=Staff.STATUS_ACTIVE) & ~Q(user_type=Staff.USER_TYPE_SYSADMIN)
        ).order_by('en_nickname')

        self.agent_contact_choices = AgentContact.objects.order_by('contact_name')
        self.project_choices = Project.objects.order_by('title')

    def clean_matter_num(self):
        matter_num = self.cleaned_data.get('matter_num', '').strip()
        return matter_num

    def clean(self):
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):
        old_matter = MatterRecord.objects.get(pk=self.instance.pk)
        clients = self.cleaned_data.get('clients', [])

        with transaction.atomic():
            matter = super(MatterEditForm, self).save(commit=False)
            matter.save()

            # add client
            matter.clients.clear()
            matter.clients.add(*clients)

            if matter.matter_type != MatterRecord.TYPE_OTHER and matter.status != MatterRecord.STATUS_CLOSED:
                update_matter_notifications(new_matter=matter, old_matter=old_matter)

        return matter

    class Meta:
        model = MatterRecord
        fields = [
            'matter_num', 'matter_type', 'matter_admin', 'subject', 'project',
            'property_street', 'property_suburb', 'property_postcode', 'property_state', 'agent_contact',
            'stamp_duty_amount', 'stamp_duty_due_date', 'stamp_duty_paid_date',
            'contract_exchange_date', 'cooling_off_date', 'settlement_date',
            'solicitor_name', 'solicitor_email', 'solicitor_mobile',
        ]


class MatterDocUploadForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.staff = kwargs.pop('staff')
        self.matter = kwargs.pop('matter')
        self.doc_dict = self.matter.make_doc_file_dict() if self.matter else {}

        self.MatterDocument = MatterDocument
        super(MatterDocUploadForm, self).__init__(*args, **kwargs)

    def save(self):

        with transaction.atomic():

            for _type, _type_desc in MatterDocument.TYPE_CHOICE:

                file_list = self.data.getlist(_type, [])
                file_notes = self.data.get(_type + '_notes', '')

                #
                # delete existed files
                #
                if len(file_list) > 0:
                    MatterDocument.objects.filter(matter=self.matter, doc_type=_type).delete()

                #
                # read tmp file, and save all files to database
                #
                for file_name in file_list:

                    global_file = GlobalFile.make_from_tmp(file_name, _type, self.matter.pk)

                    matter_doc = MatterDocument()
                    matter_doc.matter = self.matter
                    matter_doc.doc_type = _type
                    matter_doc.global_file = global_file
                    matter_doc.notes = file_notes
                    matter_doc.save()

        return self.matter


class MatterMemoUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):

        self.staff = kwargs.pop('staff')

        super(MatterMemoUpdateForm, self).__init__(*args, **kwargs)

    def clean(self):
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        matter = super(MatterMemoUpdateForm, self).save(commit=False)
        matter.save()

        return matter

    class Meta:
        model = MatterRecord
        fields = [
            'memo',
        ]


class MatterNotificationCreateForm(ModelForm):

    attachments = forms.ModelMultipleChoiceField(queryset=None, required=False)
    send_tos = forms.ModelMultipleChoiceField(queryset=None)
    cc_tos = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        self.matter = kwargs.pop('matter')
        self.MatterNotification = MatterNotification
        self.NConst = NConst
        super(MatterNotificationCreateForm, self).__init__(*args, **kwargs)

        self.receivers = NReceiver.objects.order_by('receiver')
        self.attach_types = AttachmentType.objects.order_by('type_name')

        self.fields['send_tos'].queryset = self.receivers
        self.fields['cc_tos'].queryset = self.receivers
        self.fields['attachments'].queryset = self.attach_types

    def clean(self):
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        send_tos = self.cleaned_data.get('send_tos', [])
        cc_tos = self.cleaned_data.get('cc_tos', [])
        attachments = self.cleaned_data.get('attachments', [])

        content = self.cleaned_data.get('content', '')
        subject = self.cleaned_data.get('subject', '')
        send_type = self.cleaned_data.get('send_type', '')

        if send_type == NConst.SEND_TYPE_EMAIL:
            content = MyNotice.render_email(subject=subject, content=content)

        mn = super(MatterNotificationCreateForm, self).save(commit=False)
        mn.matter = self.matter
        mn.expect_sent_at = datetime.datetime.now()
        mn.status = MatterNotification.STATUS_WAITING
        mn.is_manual = True
        mn.created_by = self.staff
        mn.content = content
        mn.save()

        # add send_tos
        mn.send_tos.add(*send_tos)

        # add cc_tos
        mn.cc_tos.add(*cc_tos)

        # add attachments
        mn.attachments.add(*attachments)

        return mn

    class Meta:
        model = MatterNotification
        fields = [
            'subject', 'content', 'send_type',
        ]
