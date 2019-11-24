import re
from django.utils.html import conditional_escape


def format_string(input, is_escape=False):
    if input is not None and isinstance(input, str):
        if is_escape:
            output = conditional_escape(input)
            output = re.sub(' +', ' ', output.strip())
        else:
            output = re.sub(' +', ' ', input.strip())
        return output
    else:
        return input
