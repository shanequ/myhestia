from __future__ import unicode_literals
import datetime
import time
from django.contrib import auth
from django.contrib.auth.views import redirect_to_login
from core.models import Staff
from myhestia import settings
from login.models import LoginSessions


class SessionExpireMiddleware(object):
    """Middleware class to timeout a session after a specified time period."""

    def process_request(self, request):
        _ = self
        #
        # only for authenticated logged in users, and not admin user
        #
        if not isinstance(request.user, Staff) or \
                not request.user.is_authenticated():
            return None

        time_stamp = time.time()
        current_datetime = datetime.datetime.fromtimestamp(time_stamp)

        login_url = settings.LOGIN_URL
        redirect_to_next = request.get_full_path()
        #
        # Timeout if idle time period is exceeded.
        #
        # Do not need to update LoginSessions modal,
        # because logout_datetime and expiry_type have already set when it was created
        #
        if 'last_activity' in request.session and \
                time_stamp - request.session['last_activity'] > settings.SESSION_IDLE_TIMEOUT:
            auth.logout(request)
            return redirect_to_login(redirect_to_next, login_url)

        #
        # Set last activity time in current session.
        #
        request.session['last_activity'] = time_stamp
        login_session = LoginSessions.objects.filter(session_key=request.session.session_key).first()
        if not login_session:
            # admin page
            return None

        login_session.logout_datetime = current_datetime + \
            datetime.timedelta(seconds=settings.SESSION_IDLE_TIMEOUT)
        login_session.save()

        return None
