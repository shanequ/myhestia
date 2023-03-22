

import re
import urllib
import urllib2


CHINA_MOBILE = re.compile(r'^861[358]\d{9}$')
AUSSIE_MOBILE = re.compile(r'(^610?4\d{8}$)|(^04\d{8}$)')
BLACK_LIST = re.compile(r'.*(\d)\1{5,}')


SMS_SP_LIST = {
    'smsglobal': {
        'url': 'https://api.smsglobal.com/http-api.php',
        'username': 'piasms',
        'password': '1yTCZSf4'
    }
}


def wash_mobile_numbers(mobile_str):

    clean_numbers = []
    dirty_numbers = []
    mobile_list = [m.strip() for m in mobile_str.split(',')]
    for t in mobile_list:
        if not t:
            continue
        target_number = filter(lambda x: x in '01234567890', t)
        if BLACK_LIST.match(target_number):
            dirty_numbers.append(t)
        elif CHINA_MOBILE.match(target_number):
            clean_numbers.append(t)
        elif AUSSIE_MOBILE.match(target_number):
            if target_number.startswith('6104'):
                clean_numbers.append('614' + target_number[4:])
            elif target_number.startswith('04'):
                clean_numbers.append('61' + target_number[1:])
            else:
                # the number is starts with 614xxxxxxxx
                clean_numbers.append(target_number)
        else:
            dirty_numbers.append(t)

    return clean_numbers, dirty_numbers


def create_api_request(message, sp='smsglobal'):
    """Create API Request based on SP name.

    Args:
        sp, String, name of the Service Provider;
        message, an object of SMS.

    Returns:
        A HTTP Request Object
    """

    if sp not in SMS_SP_LIST:
        return None
    else:
        sp_details = SMS_SP_LIST[sp]

    valid_list, _ = wash_mobile_numbers(message.target_numbers)

    if valid_list:
        targets = ','.join(valid_list)
    else:
        return None

    # Triple encode the text
    body_text = urllib.quote(message.sms_text.encode('utf8'))
    body_text = urllib.quote(body_text)
    # body_text = urllib.urlencode({'text': body_text})[5:]

    data = urllib.urlencode({'user': sp_details['username'], 'password': sp_details['password'],
                             'from': message.sms_from, 'to': targets,
                             'text': body_text, 'maxsplit': 30,
                             'action': 'sendsms'})

    return urllib2.Request(sp_details['url'], data)
