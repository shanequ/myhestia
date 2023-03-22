from __future__ import unicode_literals
from django.db.models import Q


def make_team_tree_dict():
    from core.models import StaffTeam

    _tree_dict = {
        'root_teams': [],
        'sub_team_dict': {},
    }

    all_teams = StaffTeam.objects.select_related('parent_team')
    for team in all_teams:
        if not team.parent_team:
            _tree_dict['root_teams'].append(team)
            continue

        _parent_team_id = team.parent_team.pk
        if _parent_team_id in _tree_dict['sub_team_dict']:
            _tree_dict['sub_team_dict'][_parent_team_id].append(team)
        else:
            _tree_dict['sub_team_dict'][_parent_team_id] = [team]

    return _tree_dict


def make_reporting_tree_dict():
    """
    Make membership tree
    {
        'root_users': [<LoginUser>, ..., <LoginUser>],      # all root users
        'sub_user_dict': {
            parent_user_id_0: [<LoginUser>, ..., <LoginUser>],    # parent user id and all it's member instances
            parent_user_id_1: [<LoginUser>, ..., <LoginUser>],
            ......
        }
    }
    """
    from core.models import Staff

    _tree_dict = {
        'root_users': [],
        'sub_user_dict': {},
    }

    _all_users = Staff.objects.filter(status=Staff.STATUS_ACTIVE,
                                      user_type__in=[Staff.USER_TYPE_STAFF]).select_related('team', 'line_manager')
    for _user in _all_users:
        if not _user.line_manager:
            _tree_dict['root_users'].append(_user)
            continue

        _parent_user_id = _user.line_manager.pk
        if _parent_user_id in _tree_dict['sub_user_dict']:
            _tree_dict['sub_user_dict'][_parent_user_id].append(_user)
        else:
            _tree_dict['sub_user_dict'][_parent_user_id] = [_user]

    return _tree_dict


def get_my_members_by_line_manager(user, include_myself=False):
    """
    Get my members by line manager
        - user might be or not a sales partner. Two ways to fetch data
        - if user is both line manager and sales partner, then return sales partner's data set

    Args:
        user: LoginUser
        include_myself: if result including myself

    Returns:

    """
    from core.models import StaffTeam, Staff
    if not isinstance(user, Staff):
        return None

    ret = [user] if include_myself else []

    _members = None
    if user.is_sales_partner():
        # teams and sub-teams
        _teams = StaffTeam.objects.filter(Q(sales_partner=user))
        _members = Staff.objects.filter(status=Staff.STATUS_ACTIVE, staff_team__in=_teams)
        if not include_myself:
            _members = _members.exclude(pk=user.pk)
            
    elif user.is_line_manager():
        _members = Staff.objects.filter(status=Staff.STATUS_ACTIVE, line_manager=user)

    if _members:
        ret.extend([m for m in _members])

    return ret


class CommonConst(object):

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_UNKNOWN = 'U'
    GENDER_CHOICE = ((GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female'), (GENDER_UNKNOWN, 'Unknown'),)

    AUS_STATE_CHOICE = (
        ('NSW', 'New South Wales'), ('VIC', 'Victoria'), ('QLD', 'Queens Land'),
        ('TAS', 'Tasmania'), ('SA', 'South Australia'), ('WA', 'West Australia'), ('NT', 'Northern Territory'),
    )
