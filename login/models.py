from __future__ import unicode_literals
import datetime
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db import models
from core.models import Staff
from my_tools.function import get_client_ip
from myhestia.settings import SESSION_IDLE_TIMEOUT
from django.contrib.sessions.models import Session
from django.contrib import auth


class LoginSessions(models.Model):

    EXPIRY_TYPE_LOGOUT = 'l'
    EXPIRY_TYPE_EXPIRED = 'e'
    EXPIRY_TYPE_LOGIN_KICKED = 'lk'
    EXPIRE_TYPE = ((EXPIRY_TYPE_EXPIRED, 'Time Expired'),
                   (EXPIRY_TYPE_LOGOUT, 'Logged Out'),
                   ('k', 'Kicked Out'),
                   (EXPIRY_TYPE_LOGIN_KICKED, 'Login Kicked Out'))
    user = models.ForeignKey('core.Staff', related_name='login_sessions')
    login_datetime = models.DateTimeField()
    logout_datetime = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, db_index=True)
    expire_type = models.CharField(max_length=2, choices=EXPIRE_TYPE, default=EXPIRY_TYPE_EXPIRED)
    is_latest = models.BooleanField(default=False)

    @staticmethod
    def init_login_session(user, request):

        # clear old sessions
        request.session.flush()

        now = datetime.datetime.now()
        old_session_keys = [s.session_key for s in LoginSessions.objects.filter(user=user, logout_datetime__gt=now)]
        Session.objects.filter(session_key__in=old_session_keys).delete()

        # login
        auth.login(request, user)

        LoginSessions.objects.filter(user=user, is_latest=True).update(is_latest=False)

        LoginSessions.objects.filter(user=user, logout_datetime__gt=now).\
            update(logout_datetime=now, expire_type=LoginSessions.EXPIRY_TYPE_LOGIN_KICKED)

        # make new login sessions
        logout_time = now + datetime.timedelta(seconds=SESSION_IDLE_TIMEOUT)
        ip_add = get_client_ip(request)
        LoginSessions.objects.create(user=user, login_datetime=now, logout_datetime=logout_time,
                                     ip_address=ip_add, is_latest=True, session_key=request.session.session_key)

    def get_duration(self):
        s = int((self.logout_datetime - self.login_datetime).total_seconds())
        hours = s / 3600
        s -= (hours * 3600)
        minutes = s / 60
        seconds = s - (minutes * 60)
        return hours, minutes, seconds


class UserLoginBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):

        if not username or not password:
            return None

        user = Staff.objects.filter(username=username).first()
        if not user:
            # admin
            user = User.objects.filter(username=username).first()

        if user and user.check_password(password):
            return user

        return None

    def get_user(self, user_id):

        user = Staff.objects.filter(pk=user_id).first()
        if not user:
            # admin
            user = User.objects.filter(pk=user_id).first()

        return user
