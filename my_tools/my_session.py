from __future__ import unicode_literals
from myhestia.privilege_const import MANAGING_DIRECTOR, PRIVILEGE_MATRIX


class MySession:

    KEY_PRIVILEGE = '__my_hestia_staff_privilege_session'

    def __init__(self):
        pass

    @staticmethod
    def set(request, key, value):
        request.session[key] = value

    @staticmethod
    def get(request, key, default_value=None):
        return request.session.get(key, default_value)

    @classmethod
    def init_privilege(cls, request):
        """
        Put staff privileges to session

        Outputs:
            request.session[PRIVILEGE_SESSION_KEY] =
            {
                'privilege_name': True/False,

                ... all privileges in PRIVILEGE_MATRIX ...
            }
        """
        perms_dict = {}

        # my positions
        my_positions = request.user.get_active_positions()
        my_pos_set = set([p.position for p in my_positions])

        # director has all privileges
        is_super = MANAGING_DIRECTOR in my_pos_set

        for privilege, position_list in PRIVILEGE_MATRIX.iteritems():
            perms_dict[privilege] = bool(set(position_list) & my_pos_set) or is_super

        # put privilege dict to session
        request.session[cls.KEY_PRIVILEGE] = perms_dict

    @classmethod
    def get_privilege(cls, request):
        return cls.get(request, cls.KEY_PRIVILEGE, {})
