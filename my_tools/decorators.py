from __future__ import unicode_literals

from functools import wraps

from django.contrib.auth.views import redirect_to_login, logout
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import available_attrs

from core.models import Staff
from my_tools.my_privilege import MyPrivilege
from myhestia import settings


def own_user_passes_test(login_url):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):

            # request to path
            user = request.user
            redirect_to_next = request.get_full_path()

            # if already logged in and not admin, then go through
            if user.is_authenticated() and isinstance(user, Staff):
                return view_func(request, *args, **kwargs)

            # if not login or admin
            logout(request)

            if request.is_ajax():
                return HttpResponse(status=401)

            return redirect_to_login(redirect_to_next, login_url)

        return _wrapped_view
    return decorator


def back_login_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = own_user_passes_test(login_url=settings.LOGIN_URL)

    if function:
        return actual_decorator(function)

    return actual_decorator


def check_staff_perm(privileges):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):

            is_allowed = MyPrivilege.check_privileges(request, privileges)

            if not is_allowed:
                if request.is_ajax():
                    return HttpResponse(status=404, content="User Permission denied")

                return render(request, '404.html', {})

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
