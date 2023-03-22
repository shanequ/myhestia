from django.conf.urls import url
from agent.views import AgentContactIndexView, AgentContactTableListView, AgentDetailView, AgentContactCreateView, \
    AgentContactEditView, AgentContactDeleteView, AgentContactCreateModalView
from myhestia.privilege_const import MATTER_CREATE, MATTER_VIEW
from my_tools.decorators import check_staff_perm, back_login_required


urlpatterns = [

    #
    # /agent/
    #
    url(r'^detail/(?P<agent_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_VIEW])(AgentDetailView.as_view())), name='agent_detail'),

    #
    # agent contact
    #
    url(r'^contact/$',
        back_login_required(check_staff_perm([MATTER_VIEW])(AgentContactIndexView.as_view())),
        name='agent_contact_index'),
    url(r'^contact/table-list/$',
        back_login_required(check_staff_perm([MATTER_VIEW])(AgentContactTableListView.as_view())),
        name='agent_contact_table_list'),

    url(r'^contact/create/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(AgentContactCreateView.as_view())),
        name='agent_contact_create'),

    url(r'^contact/create-modal/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(AgentContactCreateModalView.as_view())),
        name='agent_contact_create_modal'),

    url(r'^contact/edit/(?P<contact_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(AgentContactEditView.as_view())),
        name='agent_contact_edit'),

    url(r'^contact/delete/(?P<contact_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(AgentContactDeleteView.as_view())),
        name='agent_contact_delete'),
]

