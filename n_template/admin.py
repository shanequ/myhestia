from django.contrib import admin

from .models import NTemplate, NReceiver, AttachmentType


class NTAdmin(admin.ModelAdmin):
    list_display = ['id', 'template_name', 'category', 'trigger', 'trigger_days', 'send_type', 'status']
    list_filter = ['status', 'trigger', 'trigger_days']


class AttachmentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'type_name']


class NReceiverAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'receiver']


admin.site.register(NTemplate, NTAdmin)
admin.site.register(AttachmentType, AttachmentTypeAdmin)
admin.site.register(NReceiver, NReceiverAdmin)

