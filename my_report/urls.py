from django.conf.urls import url
from my_report.views import ReportStampDutyNotificationDownloadView
from my_tools.decorators import check_staff_perm, back_login_required
from myhestia.privilege_const import REPORT_VIEW


urlpatterns = [

    #
    # /report/
    #

    # stamp duty notification
    url(r'^stamp-duty-notification-download/$',
        back_login_required(check_staff_perm([REPORT_VIEW])(ReportStampDutyNotificationDownloadView.as_view())),
        name='report_stamp_duty_notification_download'),

]