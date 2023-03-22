from django.conf.urls import url
from myhestia.privilege_const import NOTIFICATION_VIEW, NOTIFICATION_CREATE
from my_tools.decorators import check_staff_perm, back_login_required
from n_template.views import NTemplateIndexView, NTemplateDetailView, NTemplatePreviewView, NTemplateEditView, \
    NTemplateInactiveView, NTemplateActiveView


urlpatterns = [

    #
    # n-template/
    #
    url(r'^template/$',
        back_login_required(check_staff_perm([NOTIFICATION_VIEW])(NTemplateIndexView.as_view())),
        name='n_template_index'),

    url(r'^template/detail/(?P<template_id>\d+)/$',
        back_login_required(check_staff_perm([NOTIFICATION_VIEW])(NTemplateDetailView.as_view())),
        name='n_template_detail'),

    url(r'^template/preview/(?P<template_id>\d+)/$',
        back_login_required(check_staff_perm([NOTIFICATION_VIEW])(NTemplatePreviewView.as_view())),
        name='n_template_preview'),


    url(r'^template/edit/(?P<template_id>\d+)/$',
        back_login_required(check_staff_perm([NOTIFICATION_CREATE])(NTemplateEditView.as_view())),
        name='n_template_edit'),
    url(r'^template/inactive/(?P<template_id>\d+)/$',
        back_login_required(check_staff_perm([NOTIFICATION_CREATE])(NTemplateInactiveView.as_view())),
        name='n_template_inactive'),
    url(r'^template/active/(?P<template_id>\d+)/$',
        back_login_required(check_staff_perm([NOTIFICATION_CREATE])(NTemplateActiveView.as_view())),
        name='n_template_active'),
]
