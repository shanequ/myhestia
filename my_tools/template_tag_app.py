from __future__ import unicode_literals
from django import template
from django.core.urlresolvers import reverse
from django.template.defaultfilters import safe
from django.utils.safestring import mark_safe
from django.utils.text import Truncator

from clientdb.models import Client
from core.models import Staff
from matters.models import MatterRecord, MatterNotification
from my_tools.function import make_btn_drop_down_html, make_a_html, make_span_html
from my_tools.function import make_drop_down_html
from my_tools.my_privilege import MyPrivilege
from my_tools.staff_auth import UserAuth
from myhestia.privilege_const import CLIENT_VIEW
from n_template.common import NConst
from n_template.models import NTemplate

register = template.Library()


#
# Staff
#
@register.simple_tag()
def user_status_bg_class(staff):
    """
        ref. bootstrap label
        for example, <span class="label label-success">Active</span>
    """
    if not isinstance(staff, Staff):
        return ''

    mapping = {
        Staff.STATUS_ACTIVE: 'label label-success',
        Staff.STATUS_INACTIVE: 'label label-default',
    }

    return mapping.get(staff.status, 'label label-default')


@register.simple_tag()
def staff_action_html(staff, request, html_type=''):
    action_list = []
    has_action = False
    next_url = request.path if not request.is_ajax() else reverse('staff_index')

    if UserAuth.can_edit_staff(staff=staff, request=request):
        has_action = True
        action_list += [
            {
                'href': "%s?next=%s" % (reverse('staff_edit', args=[staff.pk]), next_url,),
                'text': "Edit",
            },
            {
                'href': reverse('staff_change_password', args=[staff.pk]),
                'text': "Change Password",
            },
        ]

    if has_action:
        action_list += [
            {'li_class': 'divider'}
        ]

    if UserAuth.can_active_staff(staff=staff, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Active",
                'data_url': reverse('staff_active', args=[staff.pk]),
                'a_class': 'active-user-btn',
            },
        ]

    if UserAuth.can_inactive_staff(staff=staff, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Inactive",
                'data_url': reverse('staff_inactive', args=[staff.pk]),
                'a_class': 'inactive-user-btn',
            },
        ]

    if UserAuth.can_delete_staff(staff=staff, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Delete",
                'data_url': reverse('staff_delete', args=[staff.pk]),
                'a_class': 'delete-user-btn',
            },
        ]

    html_func = make_drop_down_html
    if html_type == 'btn':
        html_func = make_btn_drop_down_html

    return html_func(action_list)


#
# Client
#
@register.simple_tag()
def client_status_bg_class(client):
    """
        ref. bootstrap label
        for example, <span class="label label-success">Active</span>
    """
    if not isinstance(client, Client):
        return ''

    mapping = {
        Client.STATUS_INACTIVE: 'label label-default',
        Client.STATUS_ACTIVE: 'label label-success',
    }

    return mapping.get(client.status, 'label label-default')


@register.simple_tag()
def client_action_html(client, request, html_type=''):
    has_action = False
    action_list = []
    next_url = request.path if not request.is_ajax() else reverse('client_index')
    if UserAuth.can_edit_client(client=client, request=request):
        has_action = True
        action_list += [
            {
                'href': "%s?next=%s" % (reverse('client_edit', args=[client.pk]), next_url,),
                'text': "Edit",
            },
        ]

    if UserAuth.can_change_client_memo(client=client, request=request):
        has_action = True
        action_list += [
            {
                'href': "%s?next=%s" % (reverse('client_memo_change', args=[client.pk]), next_url,),
                'text': "Update Memo",
            },
        ]

    if has_action:
        action_list += [
            {'li_class': 'divider'}
        ]

    if UserAuth.can_inactive_client(client=client, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Inactive",
                'data_url': reverse('client_inactive', args=[client.pk]),
                'a_class': 'inactive-client-btn',
            },
        ]

    if UserAuth.can_active_client(client=client, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Active",
                'data_url': reverse('client_active', args=[client.pk]),
                'a_class': 'active-client-btn',
            },
        ]

    if UserAuth.can_delete_client(client=client, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Delete",
                'data_url': reverse('client_delete', args=[client.pk]),
                'a_class': 'delete-client-btn',
            },
        ]

    html_func = make_drop_down_html
    if html_type == 'btn':
        html_func = make_btn_drop_down_html

    return html_func(action_list)


#
# agent
#
@register.simple_tag()
def agent_contact_action_html(contact, request, html_type=''):
    action_list = []
    next_url = request.path if not request.is_ajax() else reverse('agent_contact_index')

    if UserAuth.can_edit_agent_contact(contact=contact, request=request):
        action_list += [
            {
                'href': "%s?next=%s" % (reverse('agent_contact_edit', args=[contact.pk]), next_url,),
                'text': "Edit",
            },
        ]

    if UserAuth.can_delete_agent_contact(contact=contact, request=request):
        action_list += [
            {'li_class': 'divider'}
        ]
        action_list += [
            {
                'href': '#',
                'text': "Delete",
                'data_url': "%s?next=%s" % (reverse('agent_contact_delete', args=[contact.pk]), next_url,),
                'a_class': 'delete-agent-contact-btn',
            },
        ]

    html_func = make_drop_down_html
    if html_type == 'btn':
        html_func = make_btn_drop_down_html

    return html_func(action_list)

#
# Matter
#
@register.simple_tag()
def matter_status_bg_class(matter):
    """
        ref. bootstrap label
        for example, <span class="label label-success">Active</span>
    """
    if not isinstance(matter, MatterRecord):
        return ''

    mapping = {
        MatterRecord.STATUS_CLOSED: 'label label-default',
        MatterRecord.STATUS_ACTIVE: 'label label-primary',
        MatterRecord.STATUS_STAMP_DUTY_PAID: 'label label-success',
    }

    return mapping.get(matter.status, 'label label-default')


@register.simple_tag()
def matter_type_class(matter):
    """
        ref. bootstrap label
        for example, <span class="label label-success">Active</span>
    """
    if not isinstance(matter, MatterRecord):
        return ''

    mapping = {
        MatterRecord.TYPE_SALE_EXISTING: 'txt-color-purple',
        MatterRecord.TYPE_PURCHASE_OFF_PLAN: 'txt-color-orangeDark',
        MatterRecord.TYPE_PURCHASE_EXISTING: 'txt-color-teal',
    }

    return mapping.get(matter.matter_type, '')


@register.filter
def matter_property_address(matter, output_type='text'):
    address_html = ''
    if output_type == 'text':
        address_html = "%s, %s, %s, %s" % (
            matter.property_street,
            matter.property_suburb.title(),
            matter.property_state.upper(),
            matter.property_postcode,
        )

    elif output_type == 'html':
        address_html = "%s<br>%s, %s, %s" % (
            matter.property_street,
            matter.property_suburb.title(),
            matter.property_state.upper(),
            matter.property_postcode,
        )

    elif output_type == 'excel':
        address_html = "%s\n%s, %s, %s" % (
            matter.property_street,
            matter.property_suburb.title(),
            matter.property_state.upper(),
            matter.property_postcode,
        )

    return mark_safe(address_html)


@register.filter()
def matter_client_desc(matter, separator=', '):
    return separator.join([c.get_short_desc() for c in matter.clients.all()])


@register.simple_tag()
def matter_client_html(matter, request, trim_length=0):
    html = ''
    for idx, client in enumerate(matter.clients.all()):
        if idx > 0:
            html += '<br>'

        if MyPrivilege.check_privilege(request, CLIENT_VIEW):
            html += make_a_html(href_url=reverse('client_detail', args=[client.pk]), text=client.get_short_desc(),
                                tooltip_title=client.get_short_desc(), trim_length=trim_length)
        else:
            html += make_span_html(text=client.get_short_desc(),
                                   tooltip_title=client.get_short_desc(), trim_length=trim_length)

    return safe(html)


@register.simple_tag()
def matter_action_html(matter, request, html_type=''):
    has_action = False
    action_list = []
    next_url = request.path if not request.is_ajax() else reverse('matter_index')

    if UserAuth.can_edit_matter(matter=matter, request=request):
        has_action = True
        action_list += [
            {
                'href': reverse('matter_edit', args=[matter.pk]),
                'text': "Edit",
            },
        ]

    if UserAuth.can_edit_matter(matter=matter, request=request):
        has_action = True
        action_list += [
            {
                'href': reverse('matter_doc_upload', args=[matter.pk]),
                'text': "Upload Doc.",
            },
        ]

    if UserAuth.can_send_matter_notification(matter=matter, request=request):
        has_action = True
        action_list += [
            {
                'href': "%s?next=%s" % (reverse('matter_notification_create', args=[matter.pk]), next_url,),
                'text': "Send Notification Manually",
            },
        ]

    if has_action:
        action_list += [
            {'li_class': 'divider'}
        ]

    if UserAuth.can_edit_matter(matter=matter, request=request):
        action_list += [
            {
                'href': "%s?next=%s" % (reverse('matter_memo_update', args=[matter.pk]), next_url,),
                'text': "Update Memo",
            },
        ]

    if UserAuth.can_close_matter(matter=matter, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Close",
                'data_url': reverse('matter_close', args=[matter.pk]),
                'a_class': 'close-matter-btn',
            },
        ]

    if UserAuth.can_active_matter(matter=matter, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Active",
                'data_url': reverse('matter_active', args=[matter.pk]),
                'a_class': 'active-matter-btn',
            },
        ]

    if UserAuth.can_stamp_duty_paid_matter(matter=matter, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Stamp Duty Paid",
                'data_url': reverse('matter_stamp_duty_paid', args=[matter.pk]),
                'a_class': 'stamp-duty-paid-matter-btn',
            },
        ]

    if UserAuth.can_delete_matter(matter=matter, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Delete",
                'data_url': reverse('matter_delete', args=[matter.pk]),
                'a_class': 'delete-matter-btn',
            },
        ]

    html_func = make_drop_down_html
    if html_type == 'btn':
        html_func = make_btn_drop_down_html

    return html_func(action_list)


#
# Notification Template
#
@register.simple_tag()
def n_template_status_bg_class(nt):
    """
        ref. bootstrap label
        for example, <span class="label label-success">Active</span>
    """
    if not isinstance(nt, NTemplate):
        return ''

    mapping = {
        NTemplate.STATUS_INACTIVE: 'label label-default',
        NTemplate.STATUS_ACTIVE: 'label label-primary',
    }

    return mapping.get(nt.status, 'label label-default')


@register.simple_tag()
def send_type_class(send_type):
    """
        ref. bootstrap label
        for example, <span class="label label-success">Active</span>
    """

    mapping = {
        NConst.SEND_TYPE_SMS: 'text-success',
        NConst.SEND_TYPE_EMAIL: '',
    }

    return mapping.get(send_type, '')


@register.simple_tag()
def n_template_category_class(nt):
    """
        ref. bootstrap label
        for example, <span class="label label-success">Active</span>
    """
    if not isinstance(nt, NTemplate):
        return ''

    mapping = {
        NTemplate.CATEGORY_MATTER_SALE_EXISTING: 'txt-color-purple',
        NTemplate.CATEGORY_MATTER_PURCHASE_OFF_PLAN: 'txt-color-orangeDark',
        NTemplate.CATEGORY_MATTER_PURCHASE_EXISTING: 'txt-color-teal',
    }

    return mapping.get(nt.category, '')


@register.simple_tag()
def n_template_action_html(nt, request, html_type=''):
    has_action = False
    action_list = []
    if UserAuth.can_edit_n_template(template=nt, request=request):
        has_action = True
        action_list += [
            {
                'href': reverse('n_template_edit', args=[nt.pk]),
                'text': "Edit",
            },
        ]

    if UserAuth.can_preview_n_template(template=nt, request=request):
        has_action = True
        action_list += [
            {
                'href': reverse('n_template_preview', args=[nt.pk]),
                'text': "Preview",
            },
        ]

    if has_action:
        action_list += [
            {'li_class': 'divider'}
        ]

    if UserAuth.can_inactive_n_template(template=nt, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Inactive",
                'data_url': reverse('n_template_inactive', args=[nt.pk]),
                'a_class': 'inactive-template-btn',
            },
        ]

    if UserAuth.can_active_n_template(template=nt, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Active",
                'data_url': reverse('n_template_active', args=[nt.pk]),
                'a_class': 'active-template-btn',
            },
        ]

    html_func = make_drop_down_html
    if html_type == 'btn':
        html_func = make_btn_drop_down_html

    return html_func(action_list)


@register.simple_tag()
def n_template_send_to_html(nt):
    _send_to_list = []
    for _send_to in nt.send_tos.all():
        _send_to_list += [_send_to.get_receiver_display()]

    _cc_to_list = []
    for _cc_to in nt.cc_tos.all():
        _cc_to_list += [_cc_to.get_receiver_display()]

    _to_html = ', '.join(_send_to_list) if _send_to_list else ''
    _cc_html = ("<i class='f11p text-muted'>cc: %s</i>" % ', '.join(_cc_to_list)) if _cc_to_list else ''

    if _to_html:
        _html = "%s%s" % (_to_html, ("<br>%s" % _cc_html) if _cc_html else '',)
    else:
        _html = _cc_html

    return safe(_html)


#
# MatterNotification
#
@register.simple_tag()
def mn_send_to_html(mn):
    _send_to_list = []
    for _send_to in mn.send_tos.all():
        _send_to_list += [_send_to.get_receiver_display()]

    _cc_to_list = []
    for _cc_to in mn.cc_tos.all():
        _cc_to_list += [_cc_to.get_receiver_display()]

    _to_html = ', '.join(_send_to_list) if _send_to_list else ''
    _cc_html = ("<i class='f11p text-muted'>cc: %s</i>" % ', '.join(_cc_to_list)) if _cc_to_list else ''

    if _to_html:
        _html = "%s%s" % (_to_html, ("<br>%s" % _cc_html) if _cc_html else '',)
    else:
        _html = _cc_html

    return safe(_html)


@register.simple_tag()
def make_mn_attachment_html(mn, trim_chars=0):
    if mn.attachments.exists():
        _desc = mn.get_attachment_desc()
        return make_span_html(text=_desc, tooltip_title=_desc, trim_length=trim_chars)

    _a_list = []
    for gf in mn.manual_attachment_gfs.all():
        _a = make_a_html(href_url=reverse('view_file', args=[gf.uuid]), text="Attachment")
        _a_list.append(_a)

    return safe('<br>'.join(_a_list))


@register.simple_tag()
def mn_status_bg_class(mn):
    """
        ref. bootstrap label
        for example, <span class="label label-success">Active</span>
    """
    if not isinstance(mn, MatterNotification):
        return ''

    mapping = {
        MatterNotification.STATUS_WAITING: 'label label-warning',
        MatterNotification.STATUS_SENT: 'label label-success',
        MatterNotification.STATUS_INACTIVE: 'label label-default',
    }

    return mapping.get(mn.status, 'label label-default')


@register.simple_tag()
def mn_action_html(mn, request, html_type=''):
    has_action = False
    action_list = []
    # next_url = request.path if not request.is_ajax() else reverse('n_template_index')

    if UserAuth.can_inactive_mn(mn=mn, request=request):
        has_action = True
        action_list += [
            {
                'href': '#',
                'text': "Inactive",
                'data_url': reverse('matter_notification_inactive', args=[mn.pk]),
                'a_class': 'inactive-notification-btn',
            },
        ]

    if UserAuth.can_active_mn(mn=mn, request=request):
        has_action = True
        action_list += [
            {
                'href': '#',
                'text': "Active",
                'data_url': reverse('matter_notification_active', args=[mn.pk]),
                'a_class': 'active-notification-btn',
            },
        ]

    if UserAuth.can_preview_mn(mn=mn, request=request):
        if has_action:
            action_list += [
                {'li_class': 'divider'}
            ]

        action_list += [
            {
                'href': reverse('matter_notification_preview', args=[mn.pk]),
                'text': "Preview",
            },
        ]

    html_func = make_drop_down_html
    if html_type == 'btn':
        html_func = make_btn_drop_down_html

    return html_func(action_list)


#
# project
#
@register.simple_tag()
def project_action_html(project, request, html_type=''):
    has_action = False
    action_list = []
    next_url = request.path if not request.is_ajax() else reverse('project_index')

    if UserAuth.can_edit_project(project=project, request=request):
        has_action = True
        action_list += [
            {
                'href': "%s?next=%s" % (reverse('project_edit', args=[project.pk]), next_url,),
                'text': "Edit",
            },
        ]

    if UserAuth.can_send_project_notification(project=project, request=request):
        has_action = True
        action_list += [
            {
                'href': "%s?next=%s" % (reverse('project_notification_create', args=[project.pk]), next_url,),
                'text': "Send Notification Manually",
            },
        ]

    if has_action:
        action_list += [
            {'li_class': 'divider'}
        ]

    if UserAuth.can_delete_project(project=project, request=request):
        action_list += [
            {
                'href': '#',
                'text': "Delete",
                'data_url': reverse('project_delete', args=[project.pk]),
                'a_class': 'delete-project-btn',
            },
        ]

    html_func = make_drop_down_html
    if html_type == 'btn':
        html_func = make_btn_drop_down_html

    return html_func(action_list)
