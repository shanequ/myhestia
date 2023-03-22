from myhestia import settings
from myhestia.global_const import WEBSITE_BU_NAME, WEBSITE_LOGO_URL, VERSION


def global_vars(request):
    return {
        'server_badge': settings.SERVER_BADGE,
        'WEBSITE_LOGO_URL': WEBSITE_LOGO_URL,
        'WEBSITE_BU_NAME': WEBSITE_BU_NAME,
        'VERSION': VERSION,
    }
