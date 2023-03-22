from __future__ import unicode_literals
from django import forms
from django.db.models import Q
from django.forms import ModelForm
from n_template.common import NConst
from n_template.models import NTemplate, NReceiver, AttachmentType


class NTemplateEditForm(ModelForm):

    attachments = forms.ModelMultipleChoiceField(queryset=None, required=False)
    send_tos = forms.ModelMultipleChoiceField(queryset=None)
    cc_tos = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        self.NTemplate = NTemplate
        self.NConst = NConst
        super(NTemplateEditForm, self).__init__(*args, **kwargs)

        self.receivers = NReceiver.objects.order_by('receiver')
        self.attach_types = AttachmentType.objects.order_by('type_name')

        self.fields['send_tos'].queryset = self.receivers
        self.fields['send_tos'].initial = [str(r.pk) for r in self.instance.send_tos.all()]

        self.fields['cc_tos'].queryset = self.receivers
        self.fields['cc_tos'].initial = [str(r.pk) for r in self.instance.cc_tos.all()]

        self.fields['attachments'].queryset = self.attach_types
        self.fields['attachments'].initial = [str(a.pk) for a in self.instance.attachments.all()]

    def clean_template_name(self):
        template_name = self.cleaned_data.get('template_name', '').strip()
        # unique
        if NTemplate.objects.filter(Q(template_name=template_name) & ~Q(pk=self.instance.pk)).exists():
            raise forms.ValidationError('Template name "%s" has already existed.' % template_name)
        return template_name

    def clean(self):
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        send_tos = self.cleaned_data.get('send_tos', [])
        cc_tos = self.cleaned_data.get('cc_tos', [])
        attachments = self.cleaned_data.get('attachments', [])

        t = super(NTemplateEditForm, self).save(commit=False)
        t.save()

        # add send_tos
        t.send_tos.clear()
        t.send_tos.add(*send_tos)

        # add cc_tos
        t.cc_tos.clear()
        t.cc_tos.add(*cc_tos)

        # add attachments
        t.attachments.clear()
        t.attachments.add(*attachments)

        return t

    class Meta:
        model = NTemplate
        fields = [
            'subject', 'content',
        ]
