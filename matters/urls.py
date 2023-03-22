from django.conf.urls import url
from matters.views import MatterIndexView, MatterDetailView, MatterCreateView, MatterEditView, \
    MatterCloseView, MatterActiveView, MatterContractDeleteView, MatterNotificationIndexView, \
    MatterNotificationTableListView, MatterNotificationDetailView, MatterNotificationCreateView, \
    MatterNotificationInactiveView, MatterNotificationActiveView, MatterNotificationPreviewView, MatterDeleteView, \
    MatterConveyingTableListView, MatterOtherTableListView, MatterDocUploadView, MatterStampDutyPaidView, \
    MatterMemoUpdateView, MatterDownloadLeapView, MatterCSVUploadView
from myhestia.privilege_const import MATTER_CREATE, MATTER_VIEW, NOTIFICATION_VIEW, NOTIFICATION_CREATE
from my_tools.decorators import check_staff_perm, back_login_required


urlpatterns = [

    #
    # /matter/
    #
    url(r'^$',
        back_login_required(check_staff_perm([MATTER_VIEW])(MatterIndexView.as_view())),
        name='matter_index'),
    url(r'^conveying-table-list/$',
        back_login_required(check_staff_perm([MATTER_VIEW])(MatterConveyingTableListView.as_view())),
        name='matter_conveying_table_list'),

    url(r'^other-table-list/$',
        back_login_required(check_staff_perm([MATTER_VIEW])(MatterOtherTableListView.as_view())),
        name='matter_other_table_list'),

    url(r'^detail/(?P<matter_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_VIEW])(MatterDetailView.as_view())),
        name='matter_detail'),

    url(r'^create/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterCreateView.as_view())),
        name='matter_create'),

    url(r'^csvupload/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterCSVUploadView.as_view())),
        name='matter_csv_upload'),

    url(r'^edit/(?P<matter_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterEditView.as_view())),
        name='matter_edit'),

    url(r'^doc/upload/(?P<matter_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterDocUploadView.as_view())),
        name='matter_doc_upload'),

    url(r'^contract/delete/(?P<matter_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterContractDeleteView.as_view())),
        name='matter_contract_delete'),

    url(r'^close/(?P<matter_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterCloseView.as_view())),
        name='matter_close'),
    url(r'^active/(?P<matter_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterActiveView.as_view())),
        name='matter_active'),
    url(r'^delete/(?P<matter_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterDeleteView.as_view())),
        name='matter_delete'),
    url(r'^stamp-duty-paid/(?P<matter_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterStampDutyPaidView.as_view())),
        name='matter_stamp_duty_paid'),

    # memo
    url(r'^memo/update/(?P<matter_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(MatterMemoUpdateView.as_view())),
        name='matter_memo_update'),

    # download excel for leap
    url(r'^download-leap/$',
        back_login_required(check_staff_perm([MATTER_VIEW])(MatterDownloadLeapView.as_view())),
        name='matter_download_leap'),

    #
    # matter notification
    #
    url(r'^notification/$',
        back_login_required(check_staff_perm([NOTIFICATION_VIEW])(MatterNotificationIndexView.as_view())),
        name='matter_notification_index'),
    url(r'^notification/table-list/$',
        back_login_required(check_staff_perm([NOTIFICATION_VIEW])(MatterNotificationTableListView.as_view())),
        name='matter_notification_table_list'),

    url(r'^notification/detail/(?P<notification_id>\d+)/$',
        back_login_required(check_staff_perm([NOTIFICATION_VIEW])(MatterNotificationDetailView.as_view())),
        name='matter_notification_detail'),

    url(r'^notification/preview/(?P<notification_id>\d+)/$',
        back_login_required(check_staff_perm([NOTIFICATION_VIEW])(MatterNotificationPreviewView.as_view())),
        name='matter_notification_preview'),

    url(r'^notification/create/(?P<matter_id>\d+)/',
        back_login_required(check_staff_perm([NOTIFICATION_CREATE])(MatterNotificationCreateView.as_view())),
        name='matter_notification_create'),

    url(r'^notification/inactive/(?P<notification_id>\d+)/$',
        back_login_required(check_staff_perm([NOTIFICATION_CREATE])(MatterNotificationInactiveView.as_view())),
        name='matter_notification_inactive'),
    url(r'^notification/active/(?P<notification_id>\d+)/$',
        back_login_required(check_staff_perm([NOTIFICATION_CREATE])(MatterNotificationActiveView.as_view())),
        name='matter_notification_active'),
]

