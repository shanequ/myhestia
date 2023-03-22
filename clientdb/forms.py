from __future__ import unicode_literals
from django import forms
from django.db.models import Q
from django.forms import ModelForm
from clientdb.models import Client
from core.commons import CommonConst
from myhestia.global_const import EXCEPTION_MOBILE, EXCEPTION_EMAIL


class ClientCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        self.Client = Client
        self.CommonConst = CommonConst
        super(ClientCreateForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().replace(' ', '')

    def clean_mobile(self):
        return self.cleaned_data.get('mobile', '').strip().replace(' ', '')

    def clean_first_name(self):
        return self.cleaned_data.get('first_name', '').strip()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name', '').strip()

    def clean(self):
        # email, mobile must be unique
        email = self.cleaned_data.get('email', '')
        mobile = self.cleaned_data.get('mobile', '')

        if Client.objects.filter(Q(email=email) & ~Q(email=EXCEPTION_EMAIL)).exists():
            raise forms.ValidationError('Client has already existed. Email is duplicated. %s' % email)

        if Client.objects.filter(Q(mobile=mobile) & ~Q(mobile=EXCEPTION_MOBILE)).exists():
            raise forms.ValidationError('Client has already existed. Mobile is duplicated. %s' % mobile)

        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        client = super(ClientCreateForm, self).save(commit=False)
        client.save()

        return client

    class Meta:
        model = Client
        fields = [
            'first_name', 'middle_name', 'last_name', 'en_nickname', 'email', 'mobile', 'dob', 'gender', 'memo',
        ]


class ClientEditForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.staff = kwargs.pop('staff')
        self.Client = Client
        self.CommonConst = CommonConst
        super(ClientEditForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().replace(' ', '')

    def clean_mobile(self):
        return self.cleaned_data.get('mobile', '').strip().replace(' ', '')

    def clean_first_name(self):
        return self.cleaned_data.get('first_name', '').strip()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name', '').strip()

    def clean(self):
        # email, mobile must be unique
        email = self.cleaned_data.get('email', '')
        mobile = self.cleaned_data.get('mobile', '')

        if Client.objects.filter(Q(email=email) & ~Q(pk=self.instance.pk) & ~Q(email=EXCEPTION_EMAIL)).exists():
            raise forms.ValidationError('Client has already existed. Email is duplicated. %s' % email)

        if Client.objects.filter(Q(mobile=mobile) & ~Q(pk=self.instance.pk) & ~Q(mobile=EXCEPTION_MOBILE)).exists():
            raise forms.ValidationError('Client has already existed. Mobile is duplicated. %s' % mobile)

        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        client = super(ClientEditForm, self).save(commit=False)
        client.save()

        return client

    class Meta:
        model = Client
        fields = [
            'first_name', 'middle_name', 'last_name', 'en_nickname', 'email', 'mobile', 'dob', 'gender', 'memo',
        ]


class ClientMemoChangeForm(ModelForm):

    def __init__(self, *args, **kwargs):

        self.staff = kwargs.pop('staff')

        super(ClientMemoChangeForm, self).__init__(*args, **kwargs)

    def clean(self):
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        client = super(ClientMemoChangeForm, self).save(commit=False)
        client.save()

        return client

    class Meta:
        model = Client
        fields = [
            'memo',
        ]

