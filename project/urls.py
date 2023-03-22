from django.conf.urls import url
from project.views import ProjectIndexView, ProjectDetailView, ProjectCreateView, ProjectEditView, \
    ProjectNotificationCreateView, ProjectDeleteView, ProjectTableListView
from myhestia.privilege_const import MATTER_CREATE, MATTER_VIEW, NOTIFICATION_CREATE
from my_tools.decorators import check_staff_perm, back_login_required


urlpatterns = [

    #
    # /project/
    #
    url(r'^$',
        back_login_required(check_staff_perm([MATTER_VIEW])(ProjectIndexView.as_view())),
        name='project_index'),
    url(r'^conveying-table-list/$',
        back_login_required(check_staff_perm([MATTER_VIEW])(ProjectTableListView.as_view())),
        name='project_table_list'),

    url(r'^detail/(?P<project_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_VIEW])(ProjectDetailView.as_view())),
        name='project_detail'),

    url(r'^create/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(ProjectCreateView.as_view())),
        name='project_create'),

    url(r'^edit/(?P<project_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(ProjectEditView.as_view())),
        name='project_edit'),

    url(r'^delete/(?P<project_id>\d+)/$',
        back_login_required(check_staff_perm([MATTER_CREATE])(ProjectDeleteView.as_view())),
        name='project_delete'),

    #
    # project notification
    #
    url(r'^notification/create/(?P<project_id>\d+)/',
        back_login_required(check_staff_perm([NOTIFICATION_CREATE])(ProjectNotificationCreateView.as_view())),
        name='project_notification_create'),
]

