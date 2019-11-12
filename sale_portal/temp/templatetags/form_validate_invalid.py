from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def form_error_helpers(context=None):
    errors = context.get('errors', [])
    error_helpers = ''
    if errors:
        for error in errors:
            error_helpers = error_helpers + '<span class ="form-text text-danger">'+error+'</span>'
    return error_helpers
