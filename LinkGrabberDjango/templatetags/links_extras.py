from django import template
import urllib

register = template.Library()
@register.filter(name='svensk')
def svensk(value): # Only one argument.
    """Converts a string into all lowercase"""
    test3 =urllib.unquote(value).decode('utf8')
    return test3
register.filter('svensk', svensk)

@register.filter(name='encode')
def encode(value): # Only one argument.
    """Converts a string into all lowercase"""

    return value.encode('base64')
register.filter('endcode', encode)

@register.filter(name='decode')
def decode(value): # Only one argument.
    """Converts a string into all lowercase"""
    return value.decode("base64")
register.filter('decode', decode)

@register.filter(name='btnactive')
def btnactive(seen, epid):
    if seen.filter(epid=epid):
        return True
    else:
        return False
register.filter('btnactive', btnactive)

def is_in(var, args):
    if args.filter(epid=var):
        return True
    return False

register.filter(is_in)