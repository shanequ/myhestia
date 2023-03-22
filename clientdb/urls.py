from django.conf.urls import url

from clientdb.views import ClientIndexView, ClientTableListView, ClientDetailView, ClientCreateView, \
    ClientCreateModalView, ClientEditView, ClientInactiveView, ClientActiveView, ClientMemoChangeView, ClientDeleteView
from myhestia.privilege_const import CLIENT_VIEW, CLIENT_CREATE
from my_tools.decorators import check_staff_perm, back_login_required


urlpatterns = [

    #
    # /client/
    #
    url(r'^$',
        back_login_required(check_staff_perm([CLIENT_VIEW])(ClientIndexView.as_view())),
        name='client_index'),
    url(r'^table-list/$',
        back_login_required(check_staff_perm([CLIENT_VIEW])(ClientTableListView.as_view())),
        name='client_table_list'),

    url(r'^detail/(?P<client_id>\d+)/$',
        back_login_required(check_staff_perm([CLIENT_VIEW])(ClientDetailView.as_view())),
        name='client_detail'),

    url(r'^create/$',
        back_login_required(check_staff_perm([CLIENT_CREATE])(ClientCreateView.as_view())),
        name='client_create'),

    url(r'^create-modal/$',
        back_login_required(check_staff_perm([CLIENT_CREATE])(ClientCreateModalView.as_view())),
        name='client_create_modal'),

    url(r'^edit/(?P<client_id>\d+)/$',
        back_login_required(check_staff_perm([CLIENT_CREATE])(ClientEditView.as_view())),
        name='client_edit'),

    url(r'^inactive/(?P<client_id>\d+)/$',
        back_login_required(check_staff_perm([CLIENT_CREATE])(ClientInactiveView.as_view())),
        name='client_inactive'),
    url(r'^active/(?P<client_id>\d+)/$',
        back_login_required(check_staff_perm([CLIENT_CREATE])(ClientActiveView.as_view())),
        name='client_active'),

    url(r'^delete/(?P<client_id>\d+)/$',
        back_login_required(check_staff_perm([CLIENT_CREATE])(ClientDeleteView.as_view())), name='client_delete'),

    # memo
    url(r'^memo/change/(?P<client_id>\d+)/$',
        back_login_required(check_staff_perm([CLIENT_CREATE])(ClientMemoChangeView.as_view())),
        name='client_memo_change'),
]
