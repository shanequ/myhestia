from __future__ import unicode_literals

from my_tools.my_session import MySession


class MyPrivilege():

    def __init__(self):
        pass

    @staticmethod
    def check_privileges(request, privilege_keys):
        """
        If any privilege is allowed, then return True
        If no privilege provided, then return True

        Args:
            privileges [<privilege_key>]

        Returns:
            True/False
        """
        if not privilege_keys:
            return True

        is_allowed = False
        auth_dict = MySession.get_privilege(request)
        for p in privilege_keys:
            is_allowed = auth_dict.get(str(p), False)
            if is_allowed:
                break

        return is_allowed

    @staticmethod
    def check_privilege(request, privilege_key):
        perms_dict = MySession.get_privilege(request)
        if not perms_dict or not privilege_key:
            return False

        return perms_dict.get(str(privilege_key), False)