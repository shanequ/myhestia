from __future__ import unicode_literals
import datetime
import time
from django.contrib import auth

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from login.models import LoginSessions
from my_tools.my_session import MySession
from my_tools.staff_auth import UserAuth


def login_view(request):

    template_name = 'login/login.html'

    if request.method != 'GET':
        raise Http404("Page does not exist")

    if request.user and request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))

    data = {
        'next': request.GET.get('next', ''),
        'login_url': reverse('login_check'),
    }

    return render(request, template_name, data)


def login_check(request):

    if request.method != 'POST' or not request.is_ajax():
        return HttpResponse("Access Error.")

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = auth.authenticate(username=username, password=password)

    #
    # validate login user
    #
    if not UserAuth.can_login(user):
        time.sleep(5)
        return HttpResponse("Please input correct Username & Password")

    # record login session
    LoginSessions.init_login_session(user, request)

    # put privileges to session
    MySession.init_privilege(request)

    return HttpResponse(request.POST.get('next', '') or reverse('home'))


def login_out(request):

    if request.method != 'GET':
        raise Http404("Page does not exist")

    LoginSessions.objects.filter(session_key=request.session.session_key).update(
        logout_datetime=datetime.datetime.now(), expire_type=LoginSessions.EXPIRY_TYPE_LOGOUT)
    auth.logout(request)
    return HttpResponseRedirect(reverse('login'))

