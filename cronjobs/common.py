from datetime import datetime


def log(script_name='', level='', msg=''):
    print '[%s][%s][%s]%s.' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                               level,
                               script_name,
                               msg)


def end(script_name='', err_msg=''):

    state_code = 0

    if err_msg != '':
        state_code = -1
        log(script_name=script_name, level='ERROR', msg=err_msg)

    exit(state_code)
