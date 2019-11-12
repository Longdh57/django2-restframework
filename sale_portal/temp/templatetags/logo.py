from django import template
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.templatetags.staticfiles import static

from sale_portal import setting_fe as settings

register = template.Library()


@register.simple_tag
def get_logo_url():
    ENVIRONMENT = settings.ENVIRONMENT
    if ENVIRONMENT == 'PRODUCT':
        return static('global_assets/images/vnpay_logo.png')
    elif ENVIRONMENT == 'TEST':
        return static('global_assets/images/vnpay_logo_test.png')
    else:
        return static('global_assets/images/vnpay_logo_local.png')


@register.simple_tag
def get_logo_width():
    ENVIRONMENT = settings.ENVIRONMENT
    if ENVIRONMENT == 'PRODUCT':
        return '6rem'
    else:
        return '8rem'


@register.simple_tag
def get_icon_env():
    ENVIRONMENT = settings.ENVIRONMENT
    if ENVIRONMENT == 'LOCAL':
        return mark_safe('<button id="myEnv" title="LOCAL" style="background-color: #ff5a00;">LOCAL</button>')
    elif ENVIRONMENT == 'TEST':
        return mark_safe('<button id="myEnv" title="TEST" style="background-color: red;">TEST</button>')
    else:
        return ''