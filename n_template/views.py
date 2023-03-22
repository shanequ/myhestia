from __future__ import unicode_literals
import json
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Template, Context
from django.urls import reverse
from django.views.generic import TemplateView
from my_tools.message import MyNotice
from n_template.common import NConst
from n_template.forms import NTemplateEditForm
from n_template.models import NTemplate


class NTemplateIndexView(TemplateView):

    template_name = 'n_template/template_index.html'

    def get(self, request, *args, **kwargs):

        templates = NTemplate.objects.all()

        data = {
            'templates': templates,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class NTemplateDetailView(TemplateView):

    template_name = 'n_template/template_detail.html'

    def get(self, request, *args, **kwargs):

        template_id = kwargs.get('template_id', 0)
        nt = get_object_or_404(NTemplate, pk=template_id)

        data = {
            'nt': nt,
            'NConst': NConst,
        }

        return render(request, self.template_name, data)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class NTemplatePreviewView(TemplateView):

    def get(self, request, *args, **kwargs):

        template_id = self.kwargs.get('template_id', 0)
        nt = get_object_or_404(NTemplate, pk=template_id)

        data = MyNotice.make_matter_notification_data(mn=None)

        html_content = Template(nt.content).render(Context(data))

        return HttpResponse(html_content)

    def post(self, request):
        _ = self, request
        raise Http404('Page does not exist')


class NTemplateEditView(TemplateView):

    template_name = 'n_template/template_edit.html'

    def get(self, request, *args, **kwargs):

        template_id = self.kwargs.get('template_id', 0)
        t = get_object_or_404(NTemplate, pk=template_id)

        form = NTemplateEditForm(staff=request.user, instance=t)

        data = {'form': form}

        return render(request, self.template_name, data)

    def post(self, request, template_id):

        t = get_object_or_404(NTemplate, pk=template_id)

        form = NTemplateEditForm(staff=request.user, data=request.POST, instance=t)

        data = {'form': form}

        # validate failed
        if not form.is_valid():
            return render(request, self.template_name, data)

        t = form.save()

        messages.success(request, "Template '%s' is updated" % t.template_name)

        return HttpResponseRedirect(reverse('n_template_detail', args=[t.pk]))


class NTemplateInactiveView(TemplateView):

    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, template_id):
        _ = self

        if not request.is_ajax() or template_id == 0:
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        t = get_object_or_404(NTemplate, id=template_id)

        NTemplate.objects.filter(pk=template_id).update(status=NTemplate.STATUS_INACTIVE)

        msg = "Template '%s' is inactivated. This template will not be used to generate notification anymore. " \
              "Existing active notifications will still be sent out on scheduled time" % t.template_name
        messages.success(request, msg)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


class NTemplateActiveView(TemplateView):

    """
        ajax post
    """
    def get(self, request, *args, **kwargs):
        raise Http404('Page does not exist')

    def post(self, request, template_id):
        _ = self

        if not request.is_ajax() or template_id == 0:
            raise Http404("Page not exists")

        data = {'status': 'ok'}

        t = get_object_or_404(NTemplate, id=template_id)

        NTemplate.objects.filter(pk=template_id).update(status=NTemplate.STATUS_ACTIVE)

        messages.success(request, "Template '%s' is activated." % t.template_name)

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
