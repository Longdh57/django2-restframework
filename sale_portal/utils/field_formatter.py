import re
from django.utils.html import conditional_escape


def format_string(input, is_escape=False):
    if not isinstance(input, str) :
        raise Exception('value is not a string')
    output = re.sub(' +', ' ', input.strip()) if input is not None else None
    if is_escape and input is not None:
        output = conditional_escape(output)
    return output
