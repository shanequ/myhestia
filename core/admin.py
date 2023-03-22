from django.contrib import admin

from .models import Staff


class StaffAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'en_nickname', 'first_name', 'last_name', 'gender', 'mobile', 'email']
    list_editable = ['status', 'mobile']
    list_filter = ['status', 'gender']
    search_fields = ['en_nickname', 'first_name', 'last_name']


admin.site.register(Staff, StaffAdmin)
