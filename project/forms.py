from __future__ import unicode_literals
import datetime
from django import forms
from django.db import transaction
from django.db.models import Q
from django.forms import ModelForm
from django.template import Template, Context, TemplateSyntaxError
from core.models import GlobalFile, Staff
from matters.common import update_matter_notifications
from matters.models import MatterRecord, MatterNotification, MatterDocument
from my_tools.message import MyNotice
from n_template.common import NConst
from n_template.models import NTemplate, NReceiver, AttachmentType
from project.models import Project


class ProjectCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        super(ProjectCreateForm, self).__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if Project.objects.filter(title=title).exists():
            raise forms.ValidationError('Project has already existed. Title is duplicated. %s' % title)

        return title

    def clean(self):
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        with transaction.atomic():
            project = super(ProjectCreateForm, self).save(commit=False)
            project.save()

        return project

    class Meta:
        model = Project
        fields = [
            'title',
        ]


class ProjectEditForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        super(ProjectEditForm, self).__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if Project.objects.filter(Q(title=title) & ~Q(pk=self.instance.pk)).exists():
            raise forms.ValidationError('Project has already existed. Title is duplicated. %s' % title)

        return title

    def clean(self):
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        with transaction.atomic():
            project = super(ProjectEditForm, self).save(commit=False)
            project.save()

        return project

    class Meta:
        model = Project
        fields = [
            'title',
        ]


class ProjectNotificationCreateForm(forms.Form):

    send_tos = forms.ModelMultipleChoiceField(queryset=None)
    subject = forms.CharField(required=False)
    content = forms.CharField()
    send_type = forms.ChoiceField(choices=NConst.SEND_TYPE_CHOICE)

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        self.project = kwargs.pop('project')
        self.MatterNotification = MatterNotification
        self.NConst = NConst
        super(ProjectNotificationCreateForm, self).__init__(*args, **kwargs)

        self.receivers = NReceiver.objects.filter(receiver=NReceiver.RECEIVER_CLIENT).order_by('receiver')

        self.fields['send_tos'].queryset = self.receivers

    def clean(self):
        content = self.cleaned_data.get('content', '')
        data = MyNotice.make_matter_notification_data(mn=None)
        try:
            Template(content).render(Context(data))
        except TemplateSyntaxError as e:
            raise forms.ValidationError('illegal character in content. %s' % e.message)

        return self.cleaned_data

    def save(self):

        send_tos = self.cleaned_data.get('send_tos', [])
        attachments = self.data.getlist('attachments', [])

        content = self.cleaned_data.get('content', '')
        subject = self.cleaned_data.get('subject', '')
        send_type = self.cleaned_data.get('send_type', '')

        if send_type == NConst.SEND_TYPE_EMAIL:
            content = MyNotice.render_email(subject=subject, content=content)

        mns = []
        with transaction.atomic():

            for matter in self.project.project_matters.all():
                mn = MatterNotification()
                mn.matter = matter
                mn.is_manual = True
                mn.send_type = send_type
                mn.expect_sent_at = datetime.datetime.now()
                mn.status = MatterNotification.STATUS_WAITING
                mn.subject = subject
                mn.content = content

                mn.created_by = self.staff
                mn.save()

                # add send_tos
                mn.send_tos.add(*send_tos)

                # add attachments
                for file_name in attachments:
                    global_file = GlobalFile.make_from_tmp(file_name, GlobalFile.TYPE_MANUAL_ATTACHMENT)
                    mn.manual_attachment_gfs.add(global_file)

                mns.append(mn)

        return mns
