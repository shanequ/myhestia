from django.contrib import admin

from login.models import LoginSessions


class LoginSessionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'ip_address', 'login_datetime', 'logout_datetime',
                    'get_expire_type_display', 'is_latest']

    list_filter = ['is_latest']
    search_fields = ['user__first_name']


admin.site.register(LoginSessions, LoginSessionsAdmin)

