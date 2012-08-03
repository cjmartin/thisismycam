from django import template

register = template.Library()

@register.filter
def possessive(value):
    """
    Returns a possessive form of a name according to English rules
    Mike returns Mike's, while James returns James'
    """
    if value[-1] == 's':
        return "%s'" % value
    return "%s's" % value