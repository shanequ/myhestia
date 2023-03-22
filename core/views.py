from __future__ import unicode_literals
import json
import os
import uuid
from wsgiref.util import FileWrapper

import datetime
from django.contrib.auth.decorators import login_required
from core.forms import UploadFileForm
from core.models import GlobalFile
from matters.models import MatterRecord, MatterNotification
from my_tools.function import get_content_type
from my_tools.staff_auth import UserAuth
from myhestia.settings import TMP_FILE_ROOT
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from core.forms import StaffTeamCreateForm, StaffTeamEditForm, \
    StaffCreateForm, StaffEditForm, MyProfileEditForm, ChangePasswordForm
from core.models import StaffTeam, Staff
from n_template.common import NConst
from n_template.models import NTemplate


class DashboardView(TemplateView):

    template_name = 'core/dashboard.html'

    def get(self, request, *args, **kwargs):

        staff = request.user

        today = datetime.date.today()
        one_month = today + datetime.timedelta(32)
        settle_matters = MatterRecord.objects.filter(status=MatterRecord.STATUS_ACTIVE,
                                                     matter_admin=staff,
                                                     settlement_date__range=[today, one_month])

        due_mns = MatterNotification.objects.filter(matter__stamp_duty_due_date__range=[today, one_month],
                                                    template_trigger=NTemplate.TRIGGER_STAMP_DUTY_DUE,
                                                    status__in=[MatterNotification.STATUS_WAITING])
        data = {
            'settle_matters': settle_matters,
            'NConst': NConst,
            'due_mns': due_mns,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class StaffIndexView(TemplateView):

    template_name = 'core/staff_index.html'

    def get(self, request, *args, **kwargs):

        team_id = request.GET.get('team_id', 0)

        staff_list = Staff.objects.exclude(user_type__in=[Staff.USER_TYPE_SYSADMIN])\
            .select_related('team').prefetch_related('staff_positions')

        if team_id:
            staff_list = staff_list.filter(team=team_id)

        teams = StaffTeam.objects.all().order_by('team_name')

        data = {
            'staff_list': staff_list,
            'teams': teams,
            'team_id': team_id,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class StaffDetailView(TemplateView):

    template_name = 'core/staff_detail.html'

    def get(self, request, *args, **kwargs):

        user_id = self.kwargs.get('user_id', 0)
        staff = get_object_or_404(Staff, pk=user_id)

        data = {
            'staff': staff,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class StaffCreateView(TemplateView):

    template_name = 'core/staff_create.html'

    def get(self, request, *args, **kwargs):

        form = StaffCreateForm(admin=request.user)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request):

        form = StaffCreateForm(data=request.POST, admin=request.user)

        data = {'form': form}

        if not form.is_valid():
            return render(request, self.template_name, data)

        staff = form.save()

        msg = "'%s' is created." % staff
        messages.success(request, msg)

        return HttpResponseRedirect(reverse('staff_index'))


class StaffEditView(TemplateView):

    template_name = 'core/staff_edit.html'

    def get(self, request, *args, **kwargs):

        user_id = self.kwargs.get('user_id', 0)
        staff = get_object_or_404(Staff, pk=user_id)

        next_url = request.GET.get('next', reverse('staff_detail', args=[staff.pk]))

        form = StaffEditForm(admin=request.user, instance=staff)

        data = {
            'form': form,
            'next': next_url,
        }

        return render(request, self.template_name, data)

    def post(self, request, user_id):

        staff = get_object_or_404(Staff, pk=user_id)

        next_url = request.GET.get('next', reverse('staff_detail', args=[staff.pk]))

        form = StaffEditForm(admin=request.user, data=request.POST, instance=staff)

        data = {
            'form': form,
            'next': next_url,
        }

        if not form.is_valid():
            return render(request, self.template_name, data)

        staff = form.save()

        messages.success(request, "%s is updated" % staff)

        return HttpResponseRedirect(next_url)


class StaffInactiveView(TemplateView):

    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, user_id=0):
        _ = self

        if not request.is_ajax() or user_id == 0:
            raise Http404("Page not exists")

        staff = get_object_or_404(Staff, pk=user_id)

        data = {'status': 'ok'}

        Staff.objects.filter(pk=user_id).update(status=Staff.STATUS_INACTIVE)

        msg = "%s is inactivated." % staff.get_full_name()
        messages.success(request, msg)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class StaffActiveView(TemplateView):

    """
        (ajax post)
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, user_id=0):
        _ = self

        if not request.is_ajax() or user_id == 0:
            raise Http404("Page not exists")

        staff = get_object_or_404(Staff, pk=user_id)

        data = {'status': 'ok'}

        # each team only has one head
        if staff.is_team_head and \
                Staff.objects.filter(status=Staff.STATUS_ACTIVE, is_team_head=True, team=staff.team).exists():
            data['status'] = 'error'
            data['message'] = 'Cannot active this staff. ' \
                              'Team (%s) has already had a team head.' % staff.team.team_name
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

        Staff.objects.filter(pk=user_id).update(status=Staff.STATUS_ACTIVE)

        msg = '%s is activated.' % staff
        messages.success(request, msg)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class StaffDeleteView(TemplateView):

    """
        delete (ajax post)
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, user_id=0):
        _ = self

        if not request.is_ajax() or user_id == 0:
            raise Http404("Page not exists")

        next_url = request.GET.get("next", reverse('staff_index'))

        staff = get_object_or_404(Staff, pk=user_id)

        data = {
            'status': 'ok',
            'next': next_url,
        }

        # check
        if staff.admin_matters.exists():
            data['status'] = 'error'
            data['message'] = 'Can NOT delete this staff. Some matter is using it.'
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

        Staff.objects.filter(pk=user_id).delete()

        messages.success(request, "Staff '%s' is deleted." % staff)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class StaffChangePasswordView(TemplateView):

    template_name = 'core/staff_change_password.html'

    def get(self, request, *args, **kwargs):

        user_id = self.kwargs.get('user_id', 0)
        staff = get_object_or_404(Staff, pk=user_id)

        # my password or has privilege
        if staff != request.user and not UserAuth.can_edit_staff(request=request, staff=staff):
            raise Http404('Page does not exist')

        form = ChangePasswordForm(admin=request.user, staff=staff)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request, user_id):

        staff = get_object_or_404(Staff, pk=user_id)

        # my password or has privilege
        if staff != request.user and not UserAuth.can_edit_staff(request=request, staff=staff):
            raise Http404('Page does not exist')

        form = ChangePasswordForm(admin=request.user, staff=staff, data=request.POST)

        data = {'form': form}

        # validate failed
        if not form.is_valid():
            return render(request, self.template_name, data)

        staff = form.save()

        messages.success(request, "Password is updated for %s" % staff)

        return HttpResponseRedirect(reverse('staff_detail', args=[staff.pk]))


class MyProfileEditView(TemplateView):

    template_name = 'core/my_profile_edit.html'

    def get(self, request, *args, **kwargs):

        form = MyProfileEditForm(instance=request.user)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request):

        form = MyProfileEditForm(data=request.POST, instance=request.user)

        data = {'form': form}

        # validate failed
        if not form.is_valid():
            return render(request, self.template_name, data)

        form.save()

        messages.success(request, "Profile is updated")

        return HttpResponseRedirect(reverse('staff_detail', args=[request.user.pk]))


class StaffTeamIndexView(TemplateView):

    template_name = 'core/staff_team_index.html'

    def get(self, request, *args, **kwargs):

        teams = []

        data = {'teams': teams}

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class StaffTeamCreateView(TemplateView):

    template_name = 'core/staff_team_create.html'

    def get(self, request, *args, **kwargs):

        form = StaffTeamCreateForm(admin=request.user)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request):

        form = StaffTeamCreateForm(admin=request.user, data=request.POST)

        data = {'form': form}

        if not form.is_valid():
            return render(request, self.template_name, data)

        team = form.save()

        msg = 'Team (%s) is created.' % team
        messages.success(request, msg)

        return HttpResponseRedirect(reverse('staff_team_index'))


class StaffTeamEditView(TemplateView):

    template_name = 'core/staff_team_edit.html'

    def get(self, request, *args, **kwargs):

        team_id = self.kwargs.get('team_id', 0)

        business_team = get_object_or_404(StaffTeam, pk=team_id)

        form = StaffTeamEditForm(admin=request.user, instance=business_team)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request, team_id):

        staff_team = get_object_or_404(StaffTeam, pk=team_id)

        form = StaffTeamEditForm(admin=request.user, data=request.POST, instance=staff_team)

        data = {'form': form}

        # validate failed
        if not form.is_valid():
            return render(request, self.template_name, data)

        team = form.save()

        msg = 'Team (%s) is updated.' % team
        messages.success(request, msg)

        return HttpResponseRedirect(reverse('staff_team_index'))


class StaffTeamDeleteView(TemplateView):

    """
        delete (ajax post)
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, team_id=0):
        _ = self

        if not request.is_ajax() or team_id == 0:
            raise Http404("Page not exists")

        staff_team = get_object_or_404(StaffTeam, pk=team_id)

        data = {'status': 'ok'}

        if StaffTeam.objects.filter(parent_team=staff_team).exists():
            data['status'] = 'error'
            data['message'] = 'You cannot delete team (%s). Some team depends on it' % staff_team
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

        if Staff.objects.filter(team=staff_team).exists():
            data['status'] = 'error'
            data['message'] = 'You cannot delete team (%s). Some staff depends on it' % staff_team
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

        StaffTeam.objects.filter(pk=team_id).delete()

        msg = 'Team (%s) is deleted.' % staff_team
        messages.success(request, msg)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


def view_file(request, file_uuid=''):
    """
    Read File from server and view file directly, not download

    Args:
        file_uuid: unique identity for Global File
        request

    Returns
        http file-content response
    """
    if not file_uuid or request.method != 'GET':
        raise Http404("Page does not exist")

    global_file = get_object_or_404(GlobalFile, uuid=file_uuid)

    # read file from server
    file_field = global_file.file
    wrapper = FileWrapper(open(file_field.name, 'rb'))

    #
    # make response
    #
    response = HttpResponse(wrapper, content_type=get_content_type(file_field.name))
    response['Content-Length'] = os.path.getsize(file_field.name)

    return response


@login_required
def upload(request):

    """
    Upload file and save to server temporary folder.
    This function is used for asynchronous upload.

    The temporary folder setting is TMP_FILE_ROOT, ref tradesman.settings

    Returns
        json string, like
        [
            'status': 'success'/'error',
            'err_msg': error message, if status is error
            'file_name': file name in temporary folder
        ]
    """

    if request.method != 'POST':
        raise Http404("Page does not exist")

    ret = {'status': 'success'}

    form = UploadFileForm(request.POST, request.FILES)

    if form.is_valid():

        field_file = form.cleaned_data['file']

        # make file name
        ext = field_file.name.split('.')[-1]
        filename = '{}.{}'.format(uuid.uuid4().hex, ext)
        full_name = os.path.join(TMP_FILE_ROOT, filename)

        # save file binary stream into temporary folder
        with open(full_name, 'wb+') as destination:
            for chunk in field_file.chunks():
                destination.write(chunk)

        # make response
        ret['file_name'] = filename
        ret['org_name'] = field_file.name
        return HttpResponse(json.dumps(ret, cls=DjangoJSONEncoder), content_type='application/json')

    ret['status'] = 'error'
    ret['err_msg'] = form.errors.as_text()

    return HttpResponse(json.dumps(ret, cls=DjangoJSONEncoder), content_type='application/json')
