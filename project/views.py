from __future__ import unicode_literals
import json
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from project.forms import ProjectEditForm, ProjectCreateForm, ProjectNotificationCreateForm
from my_tools.datatables import DataTableListView
from my_tools.function import make_a_html, make_div
from my_tools.template_tag_app import project_action_html
from n_template.common import NConst
from project.models import Project


class ProjectIndexView(TemplateView):

    template_name = 'project/project_index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class ProjectTableListView(DataTableListView):

    table_columns = [
        'pk', 'title', '', '',
    ]

    def get_return_row(self, project, request):

        id_html = project.pk

        matter_cnt = project.project_matters.count()
        matter_cnt_html = make_div('text-center', matter_cnt)

        title_html = make_a_html(href_url=reverse('project_detail', args=[project.pk]),
                                 text=project.title, tooltip_title=project.title, trim_length=40)

        action_html = project_action_html(project=project, request=request)

        return_list = [
            id_html,
            title_html,
            matter_cnt_html,
            action_html,
        ]

        return return_list

    def get_object_list(self, request, order_list):

        title = request.GET.get('sSearch', '')

        if title != '':
            result = Project.objects.filter(title__icontains=title)
        else:
            result = Project.objects.all()

        return result.order_by(*order_list)


class ProjectDetailView(TemplateView):

    template_name = 'project/project_detail.html'

    def get(self, request, *args, **kwargs):

        project_id = self.kwargs.get('project_id', 0)
        project = get_object_or_404(Project, pk=project_id)

        conveying_matters = project.get_conveying_matters()
        other_matters = project.get_other_matters()
        mns = project.get_mns()

        data = {
            'project': project,
            'NConst': NConst,
            'conveying_matters': conveying_matters,
            'other_matters': other_matters,
            'mns': mns,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class ProjectCreateView(TemplateView):

    template_name = 'project/project_create.html'

    def get(self, request, *args, **kwargs):

        form = ProjectCreateForm(staff=request.user)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request):

        form = ProjectCreateForm(data=request.POST, staff=request.user)

        data = {'form': form}

        if not form.is_valid():
            return render(request, self.template_name, data)

        project = form.save()

        messages.success(request, "Project(%s) is created." % project.title)
        return HttpResponseRedirect(reverse('project_index'))


class ProjectEditView(TemplateView):

    template_name = 'project/project_edit.html'

    def get(self, request, *args, **kwargs):

        project_id = self.kwargs.get('project_id', 0)
        project = get_object_or_404(Project, pk=project_id)

        next_url = request.GET.get("next", reverse('project_detail', args=[project.pk]))

        form = ProjectEditForm(staff=request.user, instance=project)

        data = {
            'form': form,
            'next': next_url,
        }

        return render(request, self.template_name, data)

    def post(self, request, project_id):

        project = get_object_or_404(Project, pk=project_id)

        next_url = request.GET.get("next", reverse('project_detail', args=[project.pk]))

        form = ProjectEditForm(staff=request.user, data=request.POST, instance=project)

        data = {
            'form': form,
            'next': next_url,
        }

        # validate failed
        if not form.is_valid():
            return render(request, self.template_name, data)

        project = form.save()

        messages.success(request, "Project (%s) is updated." % project.title)

        return HttpResponseRedirect(next_url)


class ProjectDeleteView(TemplateView):
    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, project_id):
        _ = self

        if not request.is_ajax() or project_id == 0:
            raise Http404("Page not exists")

        next_url = request.GET.get("next", reverse('project_index'))

        data = {
            'status': 'ok',
            'next': next_url,
        }

        project = get_object_or_404(Project, pk=project_id)

        Project.objects.filter(pk=project_id).delete()

        messages.success(request, "Project (%s) is deleted." % project.title)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class ProjectNotificationCreateView(TemplateView):

    template_name = 'project/project_notification_create.html'

    def get(self, request, *args, **kwargs):

        project_id = self.kwargs.get('project_id', 0)
        project = get_object_or_404(Project, pk=project_id)

        next_url = request.GET.get('next', reverse('project_detail', args=[project_id]))

        form = ProjectNotificationCreateForm(staff=request.user, project=project)

        data = {
            'form': form,
            'next': next_url,
        }

        return render(request, self.template_name, data)

    def post(self, request, project_id):

        project = get_object_or_404(Project, pk=project_id)
        next_url = request.GET.get('next', reverse('project_detail', args=[project_id]))

        form = ProjectNotificationCreateForm(data=request.POST, staff=request.user, project=project)

        data = {
            'form': form,
            'next': next_url,
        }

        if not form.is_valid():
            return render(request, self.template_name, data)

        mns = form.save()

        msg = "%s notifications for project (%s) is created and will be sent as soon as possible." % \
              (len(mns), project.title)
        messages.success(request, msg)

        return HttpResponseRedirect(next_url)
