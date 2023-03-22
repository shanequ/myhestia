from django.contrib import admin
from .models import MPEmail, SMS


class MPEAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'subject', 'insert_time', 'sent_out_time']
    search_fields = ['id', 'subject']
    list_filter = ['status']


class SMSAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'insert_time', 'sms_from', 'target_count']


admin.site.register(SMS, SMSAdmin)
admin.site.register(MPEmail, MPEAdmin)
