from __future__ import unicode_literals
import json
import os
import urllib
import urllib2
import datetime
from dateutil.relativedelta import relativedelta
from django.template.defaultfilters import safe
from django.utils.text import Truncator


def create_file(full_path, file_content):
    file_dir, file_name = os.path.split(full_path)
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    new_file = open(full_path, 'w')
    new_file.write(file_content)
    new_file.close()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_content_type(file_name=''):
    mapping = {
        'doc': 'application/msword',
        'pdf': 'application/pdf',
        'xls': 'application/vnd.ms-excel',
        'ppt': 'application/vnd.ms-powerpoint',
        'zip': 'application/zip',

        'bmp': 'image/bmp',
        'gif': 'image/gif',
        'ief': 'image/ief',
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'jpe': 'image/jpeg',
        'png': 'image/png',
        'tiff': 'image/tiff',
        'tif': 'image/tiff',
        'djvu': 'image/vnd.djvu',
        'djv': 'image/vnd.djvu',
        'wbmp': 'image/vnd.wap.wbmp',
        'ras': 'image/x-cmu-raster',
        'pnm': 'image/x-portable-anymap',
        'pbm': 'image/x-portable-bitmap',
        'pgm': 'image/x-portable-graymap',
        'ppm': 'image/x-portable-pixmap',
        'rgb': 'image/x-rgb',
        'xbm': 'image/x-xbitmap',
        'xpm': 'image/x-xpixmap',
        'xwd': 'image/x-xwindowdump',

        'html': 'text/html',
        'htm': 'text/html',
        'asc': 'text/plain',
        'csv': 'text/csv',
        'txt': 'text/plain',
        'rtx': 'text/richtext',
        'rtf': 'text/rtf',
        'xsl': 'text/xml',
        'xml': 'text/xml',

        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xltx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
        'potx': 'application/vnd.openxmlformats-officedocument.presentationml.template',
        'ppsx': 'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'sldx': 'application/vnd.openxmlformats-officedocument.presentationml.slide',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'dotx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
        'xlam': 'application/vnd.ms-excel.addin.macroEnabled.12',
        'xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
    }

    ext = file_name.split('.')[-1].lower().strip()
    content_type = mapping.get(ext, 'application/octet-stream')

    return content_type


def is_url_valid(url=''):
    try:
        if not url or urllib2.urlopen(url).code != 200:
            return ''

        return url

    except urllib2.HTTPError, urllib2.ValueError:
        return ''


def is_float(str_num=''):
    try:
        float(str_num)
        return True
    except ValueError:
        return False


def is_int(str_num=''):
    try:
        int(str_num)
        return True
    except ValueError:
        return False


def separate_every_n_characters(n, separator, st):
    string_list = [st[start - n if start - n >= 0 else 0:start] for start in reversed(range(len(st), 0, -n))]
    return separator.join(string_list)


def make_span_html(text, tooltip_title='', trim_length=0, css_class=''):
    """
    <span rel="tooltip" data-placement="bottom" data-html="true"
            data-original-title="title">
        text ...
    </span>
    """
    tooltip_str = ''
    if tooltip_title:
        tooltip_str = "rel='tooltip' " \
                      "data-placement='bottom' " \
                      "data-html='true' " \
                      "data-original-title='%s'" % tooltip_title

    class_str = ''
    if css_class:
        class_str = "class='%s'" % css_class

    html_str = '<span %s %s>%s</span>' % (class_str, tooltip_str,
                                          Truncator(text).chars(trim_length) if trim_length > 0 else text,)

    return safe(html_str)


def make_a_html(href_url, text, css_class='', trim_length=0, tooltip_title='', new_window=False):
    """
    <a href="url" rel="tooltip" data-placement="bottom" data-html="true"
        data-original-title="tooltip_title">
        text
    </a>
    """
    tooltip_str = ''
    if tooltip_title:
        tooltip_str = "rel='tooltip' " \
                      "data-placement='bottom' " \
                      "data-html='true' " \
                      "data-original-title='%s'" % tooltip_title

    class_str = ''
    if css_class:
        class_str = "class='%s'" % css_class

    html_str = '<a href="%s" %s %s %s>%s</a>' % (href_url, class_str, tooltip_str,
                                                 'target="_blank"' if new_window else '',
                                                 Truncator(text).chars(trim_length) if trim_length > 0 else text,)

    return safe(html_str)


def make_drop_down_html(li_list):
    """
    <div class="text-center">
        <div class="btn-group display-inline text-align-left">
            <button class="btn btn-xs btn-default txt-color-greenDark dropdown-toggle" data-toggle="dropdown">
                <i class="fa fa-caret-down fa-lg"></i>
            </button>
            <ul class="dropdown-menu">
                <li>
                    <a href="" class="delete-asset-btn" data-url="%s" >Delete</a>
                    <button data-toggle="modal" data-target="#notes_create_modal" class="btn btn-primary btn-sm">
                            +Add Notes
                    </button>
                </li>
            </ul>
        </div>
    </div>

    """
    li_str = ''
    if not li_list:
        return ''

    for li in li_list:
        li_class_str = "class='%s'" % li['li_class'] if 'li_class' in li else ''
        a_class_str = "class='%s'" % li['a_class'] if 'a_class' in li else ''
        data_url_str = "data-url='%s'" % li['data_url'] if 'data_url' in li else ''
        data_model_str = "data-toggle='modal' data-target='%s'" % li['data-modal-target'] \
            if 'data-modal-target' in li else ''

        a_str = "<a href='%s' %s %s %s>%s</a>" % \
                (li['href'], a_class_str, data_url_str, data_model_str, li['text']) if 'href' in li else ''

        li_str += "<li %s>%s</li>" % (li_class_str, a_str,)

    html_str = "<div class='text-center'>" \
               "   <div class='btn-group display-inline text-align-left'>" \
               "       <button class='btn btn-xs btn-default txt-color-greenDark dropdown-toggle ' " \
               "                data-toggle='dropdown'>" \
               "           <i class='fa fa-caret-down fa-lg'></i>" \
               "       </button>" \
               "       <ul class='dropdown-menu pull-right'>%s</ul>" \
               "   </div>" \
               "</div>" % li_str

    return safe(html_str)


def make_btn_drop_down_html(li_list):
    """
    <div class="btn-group">
        <button aria-expanded="false" class="button button-small button-flat-primary dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-gear"></i> Actions <span class="caret"></span>
        </button>
        <ul class="dropdown-menu">
            <li>
                <a data-toggle="modal" data-target="#remoteModal"  href="{% url ">Upload Project Image</a>
            </li>
        </ul>
    </div>

    """
    li_str = ''
    if not li_list:
        return ''

    for li in li_list:
        li_class_str = "class='%s'" % li['li_class'] if 'li_class' in li else ''
        a_class_str = "class='%s'" % li['a_class'] if 'a_class' in li else ''
        data_url_str = "data-url='%s'" % li['data_url'] if 'data_url' in li else ''
        data_model_str = "data-toggle='modal' data-target='%s'" % li['data-modal-target'] \
            if 'data-modal-target' in li else ''

        a_str = "<a href='%s' %s %s %s>%s</a>" % \
                (li['href'], a_class_str, data_url_str, data_model_str, li['text']) if 'href' in li else ''

        li_str += "<li %s>%s</li>" % (li_class_str, a_str,)

    html_str = \
        "<div class='btn-group'>" \
        "   <button aria-expanded='false' class='button button-small button-flat-primary " \
        "           dropdown-toggle' data-toggle='dropdown'>" \
        "       <i class='fa fa-gear'></i> Actions <span class='caret'></span>" \
        "   </button>" \
        "   <ul class='dropdown-menu pull-right'>%s</ul>" \
        "</div>" % li_str

    return safe(html_str)


def text_align(align_type='left', html_content=''):
    return '<div class="text-%s">%s</div>' % (align_type, html_content,)


def make_div(css_class='', content=''):
    return '<div class="%s">%s</div>' % (css_class, content,)


def make_switch_html(input_id, class_name, action_url, checked=False, on_text='ON', off_text='OFF'):
    """
    <span class="onoffswitch">
        <input type="checkbox" name="start_interval" class="onoffswitch-checkbox" id="start_interval">
        <label class="onoffswitch-label" for="start_interval">
            <span class="onoffswitch-inner" data-swchon-text="ON" data-swchoff-text="OFF"></span>
            <span class="onoffswitch-switch"></span>
        </label>
    </span>
    """
    html_str = \
        "<span class='onoffswitch'>" \
        "   <input type='checkbox' id='%s' name='onoffswitch' class='onoffswitch-checkbox %s' data-url='%s' %s>" \
        "   <label class='onoffswitch-label' for='%s'>" \
        "       <span class='onoffswitch-inner' data-swchon-text='%s' data-swchoff-text='%s'></span>" \
        "       <span class='onoffswitch-switch'></span>" \
        "   </label>" \
        "</span>" % (input_id, class_name, action_url, 'checked' if checked else '', input_id, on_text, off_text,)

    return safe(html_str)


def make_youtube_url(media_video_id=''):
    """
    Make YouTube thumbnail url and video url. formats:
        thumbnail   - http://img.youtube.com/vi/3LPDd23wTA4/0.jpg
        video       - https://www.youtube.com/embed/3LPDd23wTA4

    Args:
        media_video_id: youtube video id

    Returns:
        thumbnail url, video url
    """
    video_url = 'https://www.youtube.com/embed/%s' % media_video_id
    thumbnail_url = 'http://img.youtube.com/vi/%s/0.jpg' % media_video_id

    return thumbnail_url, video_url


def make_you_ku_url(media_video_id=''):
    """
    Make YouKu thumbnail url and video url. ref.:
        https://openapi.youku.com/v2/videos/show.json?client_id=d71d48f5539b1308&video_id=

    Args:
        media_video_id: you ku video id

    Returns:
        thumbnail url, video url
    """
    url = 'https://openapi.youku.com/v2/videos/show.json'
    param = {
        'client_id': 'd71d48f5539b1308',
        'video_id': media_video_id,
    }

    try:
        req = urllib2.Request(url, urllib.urlencode(param))
        response = urllib2.urlopen(req)
        data = json.load(response)

        video_url = data.get('player', '')
        thumbnail_url = data.get('thumbnail', '')

    except (urllib2.HTTPError, urllib2.URLError):
        thumbnail_url, video_url = '', ''

    return thumbnail_url, video_url


def get_period_range(period_date, period_type='half_year'):
    """
    Get period start date and end date <datetime.date>

    Args:
        period_date: a date in this period
        period_type:

    Returns:
        (period_start_date, period_end_date)
    """

    start_date, end_date = None, None
    if period_type == 'half_year':
        if period_date.month < 7:
            start_date = datetime.date(period_date.year, 1, 1)
            end_date = datetime.date(period_date.year, 6, 30)
        else:
            start_date = datetime.date(period_date.year, 7, 1)
            end_date = datetime.date(period_date.year, 12, 31)

    elif period_type == 'month':
        start_date = datetime.date(period_date.year, period_date.month, 1)
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)

    return start_date, end_date


def format_bank(bank_name, account_name, bsb, account_no, delimiter=', '):
    if not account_no or not bsb:
        return ''
    return "%s%s%s & %s%s%s" % (account_name, delimiter, bsb, account_no, delimiter, bank_name,)
