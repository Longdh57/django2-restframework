from sale_portal import setting_fe as settings
from django import template

register = template.Library()


@register.simple_tag
def get_api_url():
    return settings.API_URL if settings.API_URL else 'http://localhost:9001'
