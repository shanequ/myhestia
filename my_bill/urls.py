from django.conf.urls import url
from my_bill.views import BillIndexView, BillIndexSMSTableListView, BillIndexEmailTableListView
from my_tools.decorators import check_staff_perm, back_login_required
from myhestia.privilege_const import REPORT_VIEW


urlpatterns = [

    #
    # /bill/
    #
    url(r'^$',
        back_login_required(check_staff_perm([REPORT_VIEW])(BillIndexView.as_view())),
        name='bill_index'),
    url(r'^sms-table-list/$',
        back_login_required(check_staff_perm([REPORT_VIEW])(BillIndexSMSTableListView.as_view())),
        name='bill_index_sms_table_list'),
    url(r'^email-table-list/$',
        back_login_required(check_staff_perm([REPORT_VIEW])(BillIndexEmailTableListView.as_view())),
        name='bill_index_email_table_list'),

]
