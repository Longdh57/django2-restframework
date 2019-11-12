from json import dumps
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def serialize_messages(context):
    """Serialize django.contrib.messages to JSON."""
    messages = context.get('messages', [])
    data = {}
    for i, message in enumerate(messages):
        data[i] = str(message)
    return dumps(data)
