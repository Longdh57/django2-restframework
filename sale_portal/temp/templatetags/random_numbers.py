import random
from django import template

register = template.Library()


@register.simple_tag
def random_float(a, b=None):
    if b is None:
        a, b = 0, a
    return round(random.uniform(a, b), 2)


@register.simple_tag
def random_int(a, b=None):
    if b is None:
        a, b = 0, a
    return random.randint(a, b)
