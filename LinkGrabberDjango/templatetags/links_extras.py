from django import template
import urllib

from LinkGrabberDjango import apigrabber

register = template.Library()
@register.filter(name='urldecode')
def urldecode(value): # Only one argument.
    test3 =urllib.unquote(value).decode('utf8')
    if test3.startswith("GoogleDrive"):
        test3 = apigrabber.decrypt(test3[12:])
        print test3
        test3 = "https://drive" + test3.replace("\\/", "/")[:-17]+"preview"
        print test3

    return test3.replace("+", "%20")
register.filter('urldecode', urldecode)

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

def status(var):
    if var == 0:
        return "Submitted"
    if var == 1:
        return "Denied"
    if var == 2:
        return "Work in Progress"
    if var == 3:
        return "Finished"
    return False

register.filter(status)

def sslimage(var):
    image = var
    if image.startswith("http://"):
        image= "https://images.weserv.nl/?url="+image[7:]


    return image


register.filter(sslimage)