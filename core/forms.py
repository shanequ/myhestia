from __future__ import unicode_literals
import datetime
from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.forms import ModelForm

from core.commons import CommonConst
from core.models import StaffTeam, Staff, StaffPosition
from myhestia.global_const import MAX_ORG_LEVEL
from myhestia.privilege_const import STAFF_POSITIONS


class StaffCreateForm(ModelForm):

    password = forms.CharField(required=False)
    confirm_password = forms.CharField(required=False)

    position_ids = forms.MultipleChoiceField(required=False, choices=STAFF_POSITIONS)

    def __init__(self, *args, **kwargs):
        #
        # data needed
        #
        self.admin = kwargs.pop('admin')
        self.Staff = Staff
        self.CommonConst = CommonConst

        super(StaffCreateForm, self).__init__(*args, **kwargs)

        self.line_managers = Staff.objects.filter(Q(status=Staff.STATUS_ACTIVE) & ~Q(user_type=Staff.USER_TYPE_SYSADMIN))
        self.staff_teams = StaffTeam.objects.order_by('team_name')

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if not username or User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username is existed')

        return username

    def clean(self):
        password = self.cleaned_data.get('password', '')
        confirm_password = self.cleaned_data.get('confirm_password', '')
        if password and password != confirm_password:
            raise forms.ValidationError('Confirmed password is not same as password')

        # each team only has one head
        staff_team = self.cleaned_data.get('team', None)
        is_team_head = self.cleaned_data.get('is_team_head', False)
        if is_team_head and Staff.objects.filter(status=Staff.STATUS_ACTIVE,
                                                 is_team_head=True, team=staff_team).exists():
            raise forms.ValidationError('Team (%s) has already had a team head.' % staff_team.team_name)

        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=False):

        password = self.cleaned_data.get('password')

        with transaction.atomic():

            staff = super(StaffCreateForm, self).save(commit=False)
            staff.set_password(password)
            staff.save()

            # positions
            for position_id in self.cleaned_data.get("position_ids", []):
                staff_position = StaffPosition()
                staff_position.staff = staff
                staff_position.position = position_id
                staff_position.is_active = True
                staff_position.save()

        return staff

    class Meta:
        model = Staff
        fields = [
            'email', 'first_name', 'last_name', 'username', 'en_nickname', 'gender',
            'line_manager', 'team', 'is_team_head', 'join_date', 'dob', 'mobile', 'personal_email', 'notes',
        ]


class StaffEditForm(ModelForm):

    password = forms.CharField(required=False)
    confirm_password = forms.CharField(required=False)

    position_ids = forms.MultipleChoiceField(required=False, choices=STAFF_POSITIONS)

    def __init__(self, *args, **kwargs):
        self.admin = kwargs.pop('admin')
        self.Staff = Staff
        self.CommonConst = CommonConst

        super(StaffEditForm, self).__init__(*args, **kwargs)
        #
        # data needed
        #
        self.Staff = Staff
        self.line_managers = Staff.objects.filter(
            Q(status=Staff.STATUS_ACTIVE) & ~Q(pk=self.instance.pk) & ~Q(user_type=Staff.USER_TYPE_SYSADMIN)
        )
        self.staff_teams = StaffTeam.objects.order_by('team_name')

        #
        # init field
        #
        self.fields['position_ids'].initial = [str(p.position) for p in self.instance.get_active_positions()]

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if not username or \
                User.objects.filter(Q(username=username) & ~Q(pk=self.instance.pk)).exists():
            raise forms.ValidationError('Username is existed')

        return username

    def clean(self):
        password = self.cleaned_data.get('password', '')
        confirm_password = self.cleaned_data.get('confirm_password', '')
        if password and password != confirm_password:
            raise forms.ValidationError('Confirmed password is not same as password')

        # each team only has one head
        staff_team = self.cleaned_data.get('team', None)
        is_team_head = self.cleaned_data.get('is_team_head', False)
        if is_team_head and \
            Staff.objects.filter(Q(status=Staff.STATUS_ACTIVE) & Q(is_team_head=True) &
                                Q(team=staff_team) & ~Q(pk=self.instance.pk)).exists():
            raise forms.ValidationError('Team (%s) has already had a team head.' % staff_team.team_name)

        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        password = self.cleaned_data.get('password')

        with transaction.atomic():
            staff = super(StaffEditForm, self).save(commit=False)
            if password:
                staff.set_password(password)

            staff.save()

            # positions
            StaffPosition.objects.filter(staff=staff).delete()
            for position_id in self.cleaned_data.get("position_ids", []):
                staff_position = StaffPosition()
                staff_position.staff = staff
                staff_position.position = position_id
                staff_position.is_active = True
                staff_position.save()

        return staff

    class Meta:
        model = Staff
        fields = [
            'email', 'first_name', 'last_name', 'username', 'en_nickname', 'gender',
            'line_manager', 'team', 'is_team_head', 'join_date', 'dob', 'mobile', 'personal_email', 'notes',
        ]


class ChangePasswordForm(forms.Form):

    password = forms.CharField(required=False)
    confirm_password = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.admin = kwargs.pop('admin')
        self.staff = kwargs.pop('staff')

        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        password = self.cleaned_data.get('password', '')
        confirm_password = self.cleaned_data.get('confirm_password', '')
        if password and password != confirm_password:
            raise forms.ValidationError('Confirmed password is not same as password')

        return self.cleaned_data

    def save(self):

        password = self.cleaned_data.get('password')

        self.staff.set_password(password)
        self.staff.save()

        return self.staff


class MyProfileEditForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(MyProfileEditForm, self).__init__(*args, **kwargs)
        self.Staff = Staff

    def clean(self):
        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        login_user = super(MyProfileEditForm, self).save(commit=False)
        login_user.save()

        return login_user

    class Meta:
        model = Staff
        fields = [
            'en_nickname', 'mobile', 'personal_email',
        ]


class StaffTeamCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):

        self.admin = kwargs.pop('admin')
        self.business_teams = StaffTeam.objects.order_by('team_name')

        super(StaffTeamCreateForm, self).__init__(*args, **kwargs)

    def clean_team_name(self):
        # be unique
        new_team_name = self.cleaned_data['team_name'].strip()
        if new_team_name == '':
            raise forms.ValidationError('Please input valid team name')

        if StaffTeam.objects.filter(team_name=new_team_name).exists():
            raise forms.ValidationError('Team name has already existed')

        return new_team_name

    def clean(self):
        # max. tree level
        parent_team = self.cleaned_data.get('parent_team', None)
        _level = parent_team.level + 1
        if _level >= MAX_ORG_LEVEL:
            raise forms.ValidationError('Maximum %s-level team structure' % MAX_ORG_LEVEL)

        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        parent_team = self.cleaned_data.get('parent_team', None)

        with transaction.atomic():
            business_team = super(StaffTeamCreateForm, self).save(commit=False)
            business_team.level = parent_team.level + 1
            business_team.save()

        return business_team

    class Meta:
        model = StaffTeam
        fields = [
            'team_name', 'parent_team',
        ]


class StaffTeamEditForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.admin = kwargs.pop('admin')
        super(StaffTeamEditForm, self).__init__(*args, **kwargs)

        self.business_teams = StaffTeam.objects.filter(~Q(pk=self.instance.pk)).order_by('team_name')

    def clean_team_name(self):
        # be unique
        team_name = self.cleaned_data['team_name'].strip()

        if StaffTeam.objects.filter(Q(team_name=team_name) & ~Q(pk=self.instance.pk)).exists():
            raise forms.ValidationError('Team name has already existed')

        return team_name

    def clean(self):
        # max. tree level
        parent_team = self.cleaned_data.get('parent_team', None)
        _level = parent_team.level + 1
        if _level >= MAX_ORG_LEVEL:
            raise forms.ValidationError('Maximum %s-level team structure' % MAX_ORG_LEVEL)

        if self.instance.child_teams.exists() and _level >= MAX_ORG_LEVEL - 1:
            raise forms.ValidationError('Maximum %s-level team structure. Sub team existed' % MAX_ORG_LEVEL)

        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):

        parent_team = self.cleaned_data.get('parent_team', None)

        business_team = super(StaffTeamEditForm, self).save(commit=False)
        business_team.level = parent_team.level + 1
        business_team.save()

        return business_team

    class Meta:
        model = StaffTeam
        fields = [
            'team_name', 'parent_team',
        ]


class UploadFileForm(forms.Form):
    """
        upload file
    """
    file = forms.FileField()
