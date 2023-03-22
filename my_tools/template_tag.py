from __future__ import unicode_literals
import json
from collections import OrderedDict

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.template.defaulttags import url
from django.utils.safestring import mark_safe

from core.commons import make_reporting_tree_dict, make_team_tree_dict, CommonConst
from my_tools.breadcrumb import BreadcrumbNode, UrlBreadcrumbNode
from my_tools.function import make_a_html, separate_every_n_characters
from my_tools.my_session import MySession
from my_tools.staff_auth import UserAuth
from myhestia import privilege_const

register = template.Library()


@register.filter
def check_pv(request, variable_name):
    """
        Get privilege dict value by variable key
    """
    d = MySession.get_privilege(request)
    # do not delete - import const
    _ = privilege_const.PRIVILEGE_MATRIX

    key = eval("privilege_const.%s" % variable_name)

    return d.get(str(key), False)


@register.simple_tag
def check_user_auth(function_name, *args, **kwargs):
    function = getattr(UserAuth, function_name)

    return function(*args, **kwargs)


@register.simple_tag
def get_message_class(message):
    """

    """
    class_name = 'alert-info'
    if not message:
        return class_name

    if message.tags == 'success':
        class_name = 'alert-success'

    elif message.tags == 'error':
        class_name = 'alert-danger'

    elif message.tags == 'warning':
        class_name = 'alert-warning'

    return class_name


@register.tag
def breadcrumb(parser, token):
    """
    Renders the breadcrumb.
    Examples:
        {% breadcrumb "Title of breadcrumb" url_var %}
        {% breadcrumb context_var  url_var %}
        {% breadcrumb "Just the title" %}
        {% breadcrumb just_context_var %}

    Parameters:
    -First parameter is the title of the crumb,
    -Second (optional) parameter is the url variable to link to, produced by url tag, i.e.:
        {% url person_detail object.id as person_url %}
        then:
        {% breadcrumb person.name person_url %}

    """
    return BreadcrumbNode(token.split_contents()[1:])


@register.tag
def breadcrumb_url(parser, token):
    """
    Same as breadcrumb
    but instead of url context variable takes in all the
    arguments URL tag takes.
        {% breadcrumb "Title of breadcrumb" person_detail person.id %}
        {% breadcrumb person.name person_detail person.id %}
    """

    bits = token.split_contents()
    if len(bits) == 2:
        return breadcrumb(parser, token)

    # Extract our extra title parameter
    title = bits.pop(1)
    token.contents = ' '.join(bits)

    url_node = url(parser, token)

    return UrlBreadcrumbNode(title, url_node)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def list2js_array(python_list):
    if not python_list:
        return "[]"
    return '["%s"]' % '","'.join(python_list)


@register.filter
def make_json(obj):
    if obj is None or obj == '':
        return ''

    return json.dumps(obj, cls=DjangoJSONEncoder)


@register.filter(name='mul')
def mul(value1=0, value2=0):
    try:
        amount1 = float(value1)
        amount2 = float(value2)
    except ValueError:
        amount1 = 0
        amount2 = 0

    return amount1 * amount2


@register.filter
def subtract(value, arg):
    return value - arg


@register.simple_tag
def money_html(amount, has_color=True, has_sign=True, has_prefix=True):
    css_class = ''
    if has_color:
        css_class = 'txt-color-green' if amount >= 0 else 'txt-color-red'

    _prefix = '$' if has_prefix else ''
    _amount = amount if has_sign else abs(amount)

    if _amount < 0 and has_prefix:
        _prefix = '-$'
        _amount = abs(amount)

    return mark_safe("<span class='%s'>%s%s</span>" % (css_class, _prefix, '{:,.2f}'.format(_amount)))


@register.simple_tag
def make_google_map_url(address):
    """
    make google map link

    Usage:
        {% make_gmap_url address %}
    """
    google_map_url = 'https://www.google.com.au/maps/place/' + address
    return google_map_url


@register.simple_tag
def make_team_tree(request, level=0, parent=None, team_dict=None):

    _level_bg_mapping = {
        0: 'label label-success',
        1: 'label label-info',
        2: 'label bg-color-pinkDark',
        3: 'label bg-color-blueLight',
    }

    staff = request.user

    if not team_dict:
        team_dict = make_team_tree_dict()

    sub_teams = team_dict['root_teams'] if not parent else team_dict['sub_team_dict'].get(parent.pk, [])
    if not sub_teams:
        return ''

    _li_html = ''
    for _sub_team in sub_teams:

        _sub_team_html = make_team_tree(request=request, level=level + 1, parent=_sub_team, team_dict=team_dict)

        _bg_color = _level_bg_mapping.get(level, '') if _sub_team_html else ''
        _icon = '<i class="fa fa-lg fa-minus-circle"></i>' if _sub_team_html else ''

        # root cannot be edited or deleted
        _edit_html, _delete_html = '', ''
        if UserAuth.can_edit_team(team=_sub_team, request=request) and level > 0:
            _edit_html = make_a_html(href_url=reverse('staff_team_edit', args=[_sub_team.pk]),
                                     text='Edit')
            _delete_html = '<a class="delete-team-btn ml5" href="#" data-url="%s">Delete</a>' % \
                           reverse('staff_team_delete', args=[_sub_team.pk])
        _li_html += \
            '<li>' \
            '    <span class="%s">%s %s</span> %s %s %s' \
            '</li>' % (_bg_color, _icon, _sub_team.team_name, _edit_html, _delete_html, _sub_team_html,)

    _html = '<ul>%s</ul>' % _li_html

    return mark_safe(_html)


@register.simple_tag
def make_staff_tree(request, level=0, parent=None, user_dict=None):

    _level_bg_mapping = {
        0: 'label label-success',
        1: 'label label-info',
        2: 'label bg-color-pinkDark',
        3: 'label bg-color-blueLight',
    }

    if not user_dict:
        user_dict = make_reporting_tree_dict()

    sub_users = user_dict['root_users'] if not parent else user_dict['sub_user_dict'].get(parent.pk, [])
    if not sub_users:
        return ''

    _li_html = ''
    for _sub_user in sub_users:

        _sub_user_html = make_staff_tree(request=request, level=level + 1, parent=_sub_user, user_dict=user_dict)

        _bg_color = _level_bg_mapping.get(level, '') if _sub_user_html else ''
        _icon = '<i class="fa fa-lg fa-minus-circle"></i>' if _sub_user_html else ''

        _edit_html, _delete_html = '', ''
        if UserAuth.can_edit_staff(staff=_sub_user, request=request):
            _edit_html = make_a_html(href_url=reverse('staff_edit', args=[_sub_user.pk]), text='Edit')
            _delete_html = '<a class="inactive-user-btn ml5" href="#" data-url="%s">Inactive</a>' % \
                           reverse('staff_inactive', args=[_sub_user.pk])
        _li_html += \
            '<li class="%s">' \
            '    <span class="%s">%s %s</span> %s %s %s' \
            '</li>' % ("mb20" if not parent else '',
                       _bg_color, _icon, _sub_user.get_short_desc(), _edit_html, _delete_html, _sub_user_html,)

    _html = '<ul>%s</ul>' % _li_html

    return mark_safe(_html)


@register.simple_tag
def get_definition_html(word=''):

    mapping_dict = {
        # sr
        'sr_list_deposit': 'Total deposit available balance (including non cash) / exchanged payment, '
                           'if SR in status reserved, contract signed and exchanged, '
                           'else it\'s trust account available balance',
        # sales advice
        'sa_save_vs_contact': 'System will auto fill these fields for next new sales advice if save them to project. '
                              'You can still change these fields manually on editing project page',

        # ta
        'available_balance': 'confirmed amount - amount pending to withdraw',
        'total_balance': 'all pending and confirmed amount',

        # listing
        'project_promote': 'If promoted, this project will be clearly marked on sales website',
        'project_promote_tag': '* if project is promoted',

        'property_promote': 'If promoted, this property will be clearly marked on sales website',

        # commission
        'cm_invoice_save_account_payable': 'System will auto fill these fields for next new invoice '
                                           'if save them to your profile.',

        # client
        'client_firb_status': 'If FIRB is unknown, the client or entity '
                              '<b class="txt-color-red">CANNOT</b> make reservation.'
    }

    return mapping_dict.get(word.strip().lower(), '')


@register.simple_tag()
def get_gender_class(gender):

    mapping = {
        CommonConst.GENDER_FEMALE: 'txt-color-pink',
        CommonConst.GENDER_MALE: 'txt-color-teal',
    }

    return mapping.get(gender, '')


@register.filter
def insert_space(string, n=3):
    return separate_every_n_characters(n, ' ', string)


@register.filter
def insert_space_mobile(string):
    str_len = len(string) if string else 0
    if not string or str_len < 6:
        return string

    return "%s %s %s" % (string[0: -6], string[-6: -3], string[-3:],)


@register.simple_tag()
def make_template_variable_help():
    from my_tools.message import MyNotice
    _v_dict = MyNotice.make_matter_notification_data()
    _v_dict = OrderedDict(sorted(_v_dict.items(), key=lambda (k, x): k))
    _help = '<br> '.join([k for k, v in _v_dict.iteritems()])

    return mark_safe(_help)
