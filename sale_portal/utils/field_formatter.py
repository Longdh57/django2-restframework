import re


def format_string(input):
    if not isinstance(input, str) :
        raise Exception('value is not a string')
    output = re.sub(' +', ' ', input.strip()) if input is not None else None
    return output
