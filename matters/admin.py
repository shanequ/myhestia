from django.contrib import admin


from .models import MatterRecord, MatterNotification


class MRAdmin(admin.ModelAdmin):
    list_display = ['id', 'matter_num', 'matter_type', 'status', 'stamp_duty_amount',
                    'stamp_duty_due_date', 'stamp_duty_paid_date']

    search_fields = ['id', 'matter_num']
    list_filter = ['matter_type', 'status']


class MNAdmin(admin.ModelAdmin):
    list_display = ['id', 'matter', 'is_manual', 'send_type', 'expect_sent_at',
                    'sent_at', 'status', 'template_category', 'template_trigger', 'template_trigger_days']

    search_fields = ['id', 'matter']
    list_filter = ['template_category', 'template_trigger', 'status']


admin.site.register(MatterRecord, MRAdmin)
admin.site.register(MatterNotification, MNAdmin)
