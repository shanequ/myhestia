from __future__ import unicode_literals

from core.models import Staff
from my_tools.my_privilege import MyPrivilege
from myhestia.privilege_const import STAFF_TEAM_CREATE, STAFF_CREATE, CLIENT_CREATE, MATTER_CREATE, \
    NOTIFICATION_CREATE, NOTIFICATION_VIEW
from n_template.common import NConst


class UserAuth(object):
    """
        app logic authentication
    """
    def __init__(self):
        super(UserAuth, self).__init__()

    @staticmethod
    def can_login(user):
        return isinstance(user, Staff) and \
            user.status == user.STATUS_ACTIVE and \
            user.get_active_positions()

    #
    # team
    #
    @staticmethod
    def can_edit_team(**kwargs):
        _ = kwargs['team']
        request = kwargs['request']
        return MyPrivilege.check_privilege(request, STAFF_TEAM_CREATE)

    #
    # staff
    #
    @staticmethod
    def can_edit_staff(**kwargs):
        _ = kwargs['staff']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, STAFF_CREATE)

    @staticmethod
    def can_active_staff(**kwargs):
        staff = kwargs['staff']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, STAFF_CREATE) and \
            staff.status == staff.STATUS_INACTIVE

    @staticmethod
    def can_inactive_staff(**kwargs):
        staff = kwargs['staff']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, STAFF_CREATE) and\
            staff.status == staff.STATUS_ACTIVE

    @staticmethod
    def can_delete_staff(**kwargs):
        _ = kwargs['staff']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, STAFF_CREATE)

    #
    # client
    #
    @staticmethod
    def can_edit_client(**kwargs):
        _ = kwargs['client']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, CLIENT_CREATE)

    @staticmethod
    def can_change_client_memo(**kwargs):
        _ = kwargs['client']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, CLIENT_CREATE)

    @staticmethod
    def can_active_client(**kwargs):
        client = kwargs['client']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, CLIENT_CREATE) and \
            client.status == client.STATUS_INACTIVE

    @staticmethod
    def can_delete_client(**kwargs):
        _ = kwargs['client']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, CLIENT_CREATE)

    @staticmethod
    def can_inactive_client(**kwargs):
        client = kwargs['client']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, CLIENT_CREATE) and \
            client.status == client.STATUS_ACTIVE

    #
    # Agent
    #
    @staticmethod
    def can_edit_agent_contact(**kwargs):
        _ = kwargs['contact']
        request = kwargs['request']
        return MyPrivilege.check_privilege(request, MATTER_CREATE)

    @staticmethod
    def can_delete_agent_contact(**kwargs):
        _ = kwargs['contact']
        request = kwargs['request']
        return MyPrivilege.check_privilege(request, MATTER_CREATE)

    #
    # Matter
    #
    @staticmethod
    def can_edit_matter(**kwargs):
        _ = kwargs['matter']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, MATTER_CREATE)

    @staticmethod
    def can_active_matter(**kwargs):
        matter = kwargs['matter']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, MATTER_CREATE) and \
            matter.status in [matter.STATUS_CLOSED, matter.STATUS_STAMP_DUTY_PAID]

    @staticmethod
    def can_stamp_duty_paid_matter(**kwargs):
        matter = kwargs['matter']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, MATTER_CREATE) and \
            matter.matter_type not in [matter.TYPE_OTHER] and \
            matter.status in [matter.STATUS_ACTIVE, matter.STATUS_CLOSED]

    @staticmethod
    def can_close_matter(**kwargs):
        matter = kwargs['matter']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, MATTER_CREATE) and \
            matter.status in [matter.STATUS_ACTIVE, matter.STATUS_STAMP_DUTY_PAID]

    @staticmethod
    def can_delete_matter(**kwargs):
        _ = kwargs['matter']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, MATTER_CREATE)

    @staticmethod
    def can_send_matter_notification(**kwargs):
        _ = kwargs['matter']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, NOTIFICATION_CREATE)

    #
    # Notification Template
    #
    @staticmethod
    def can_edit_n_template(**kwargs):
        _ = kwargs['template']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, NOTIFICATION_CREATE)

    @staticmethod
    def can_preview_n_template(**kwargs):
        _ = kwargs['template']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, NOTIFICATION_VIEW)

    @staticmethod
    def can_active_n_template(**kwargs):
        template = kwargs['template']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, NOTIFICATION_CREATE) and \
            template.status == template.STATUS_INACTIVE

    @staticmethod
    def can_inactive_n_template(**kwargs):
        template = kwargs['template']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, NOTIFICATION_CREATE) and \
            template.status == template.STATUS_ACTIVE

    #
    # MatterNotification
    #
    @staticmethod
    def can_preview_mn(**kwargs):
        _ = kwargs['mn']
        request = kwargs['request']

        # sms do not need to preview
        return MyPrivilege.check_privilege(request, NOTIFICATION_VIEW)

    @staticmethod
    def can_edit_mn(**kwargs):
        notification = kwargs['mn']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, NOTIFICATION_CREATE) and \
            notification.status in [notification.STATUS_INACTIVE, notification.STATUS_WAITING] and \
            notification.generated_type == notification.GENERATED_TYPE_MANUAL

    @staticmethod
    def can_inactive_mn(**kwargs):
        notification = kwargs['mn']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, MATTER_CREATE) and \
            notification.status == notification.STATUS_WAITING

    @staticmethod
    def can_active_mn(**kwargs):
        notification = kwargs['mn']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, MATTER_CREATE) and \
            notification.status == notification.STATUS_INACTIVE

    #
    # Project
    #
    @staticmethod
    def can_edit_project(**kwargs):
        _ = kwargs['project']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, MATTER_CREATE)

    @staticmethod
    def can_delete_project(**kwargs):
        _ = kwargs['project']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, MATTER_CREATE)

    @staticmethod
    def can_send_project_notification(**kwargs):
        _ = kwargs['project']
        request = kwargs['request']

        return MyPrivilege.check_privilege(request, NOTIFICATION_CREATE)
