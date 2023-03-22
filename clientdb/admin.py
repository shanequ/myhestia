from django.contrib import admin

from .models import Client


class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'middle_name', 'last_name', 'en_nickname', 'email', 'mobile']
    search_fields = ['first_name', 'last_name', 'email', 'mobile']


admin.site.register(Client, ClientAdmin)

