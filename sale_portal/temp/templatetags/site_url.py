from django import template
from sale_portal import setting_fe as settings

register = template.Library()


@register.simple_tag
def get_site_url():
    return settings.SITE_URL if settings.SITE_URL else 'http://localhost:9002'
