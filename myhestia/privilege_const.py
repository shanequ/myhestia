from __future__ import unicode_literals
"""
    Privilege for back office
"""

# Staff Position Name
MANAGING_DIRECTOR = 1

# business manager
BM_ADMIN_MANAGER = 21


#
# system position, alphabetical
#
STAFF_POSITIONS = (
    (BM_ADMIN_MANAGER, 'Business Manager'),
    (MANAGING_DIRECTOR, 'Managing Director'),
)


#
# system privilege
#

#
# staff
#
STAFF_VIEW = 'STAFF_VIEW'
# create, edit, active, inactive
STAFF_CREATE = 'STAFF_CREATE'

#
# staff team
#
STAFF_TEAM_VIEW = 'STAFF_TEAM_VIEW'
# create, edit, delete
STAFF_TEAM_CREATE = 'STAFF_TEAM_CREATE'

#
# client
#
CLIENT_VIEW = 'CLIENT_VIEW'
# create, edit, delete, active, inactive
CLIENT_CREATE = 'CLIENT_CREATE'

#
# matter
#
MATTER_VIEW = 'MATTER_VIEW'
MATTER_CREATE = 'MATTER_CREATE'

#
# notification
#

# template
NOTIFICATION_VIEW = 'NOTIFICATION_VIEW'
NOTIFICATION_CREATE = 'NOTIFICATION_CREATE'

#
# report
#
REPORT_VIEW = 'REPORT_VIEW'

#
# dashboard
#
DASHBOARD_SALES_PERFORMANCE = 'DASHBOARD_SALES_PERFORMANCE'


PRIVILEGE_MATRIX = {
    # staff
    STAFF_VIEW: [BM_ADMIN_MANAGER],
    STAFF_CREATE: [BM_ADMIN_MANAGER],

    # team
    STAFF_TEAM_VIEW: [BM_ADMIN_MANAGER],
    STAFF_TEAM_CREATE: [BM_ADMIN_MANAGER],

    # client
    CLIENT_VIEW: [BM_ADMIN_MANAGER],
    CLIENT_CREATE: [BM_ADMIN_MANAGER],

    # matter
    MATTER_VIEW: [BM_ADMIN_MANAGER],
    MATTER_CREATE: [BM_ADMIN_MANAGER],

    # notification template
    # notification
    NOTIFICATION_VIEW: [BM_ADMIN_MANAGER],
    NOTIFICATION_CREATE: [BM_ADMIN_MANAGER],

    # report
    REPORT_VIEW: [BM_ADMIN_MANAGER],

    # dashboard
    DASHBOARD_SALES_PERFORMANCE: [BM_ADMIN_MANAGER],

}
