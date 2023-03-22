#
#  System smoke test
#


import pytest
import os

@pytest.fixture(scope='module')
def expected_sys_test_result():
    r = os.environ.get('EXP_SYS_RESULT', 'OK')
    if r == 'OK':
        return True
    return False


def test_system(expected_sys_test_result):
    assert expected_sys_test_result

