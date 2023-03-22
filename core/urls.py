from django.conf.urls import url

from core.views import DashboardView, StaffTeamIndexView, StaffTeamCreateView, StaffTeamEditView, StaffTeamDeleteView, \
    StaffIndexView, StaffDetailView, StaffCreateView, StaffEditView, StaffInactiveView, StaffActiveView, \
    StaffChangePasswordView, MyProfileEditView, StaffDeleteView
from my_tools.decorators import back_login_required, check_staff_perm
from myhestia.privilege_const import STAFF_VIEW, STAFF_CREATE, STAFF_TEAM_VIEW, STAFF_TEAM_CREATE


urlpatterns = [
    #
    # /back-office/home
    #
    url(r'^$', back_login_required(check_staff_perm([])(DashboardView.as_view())), name='home'),

    #
    # business team
    #
    url(r'^staff-team/$',
        back_login_required(check_staff_perm([STAFF_TEAM_VIEW])(StaffTeamIndexView.as_view())),
        name='staff_team_index'),
    url(r'^staff-team/create/$',
        back_login_required(check_staff_perm([STAFF_TEAM_CREATE])(StaffTeamCreateView.as_view())),
        name='staff_team_create'),
    url(r'^staff-team/edit/(?P<team_id>\d+)/$',
        back_login_required(check_staff_perm([STAFF_TEAM_CREATE])(StaffTeamEditView.as_view())),
        name='staff_team_edit'),
    url(r'^staff-team/delete/(?P<team_id>\d+)/$',
        back_login_required(check_staff_perm([STAFF_TEAM_CREATE])(StaffTeamDeleteView.as_view())),
        name='staff_team_delete'),

    #
    # staff
    #
    url(r'^staff/$',
        back_login_required(check_staff_perm([STAFF_VIEW])(StaffIndexView.as_view())),
        name='staff_index'),
    url(r'^staff-detail/(?P<user_id>\d+)/$',
        back_login_required(check_staff_perm([STAFF_VIEW])(StaffDetailView.as_view())),
        name='staff_detail'),
    url(r'^staff/create/$',
        back_login_required(check_staff_perm([STAFF_CREATE])(StaffCreateView.as_view())),
        name='staff_create'),
    url(r'^staff/edit/(?P<user_id>\d+)/$',
        back_login_required(check_staff_perm([STAFF_CREATE])(StaffEditView.as_view())),
        name='staff_edit'),
    url(r'^staff/inactive/(?P<user_id>\d+)/$',
        back_login_required(check_staff_perm([STAFF_CREATE])(StaffInactiveView.as_view())),
        name='staff_inactive'),
    url(r'^staff/active/(?P<user_id>\d+)/$',
        back_login_required(check_staff_perm([STAFF_CREATE])(StaffActiveView.as_view())),
        name='staff_active'),
    url(r'^staff/delete/(?P<user_id>\d+)/$',
        back_login_required(check_staff_perm([STAFF_CREATE])(StaffDeleteView.as_view())),
        name='staff_delete'),

    # change password for me or other staff
    url(r'^staff/change-password/(?P<user_id>\d+)/$',
        back_login_required(check_staff_perm([])(StaffChangePasswordView.as_view())),
        name='staff_change_password'),

    # edit my profile
    url(r'^staff/my-edit/$',
        back_login_required(check_staff_perm([])(MyProfileEditView.as_view())),
        name='my_profile_edit'),

]
