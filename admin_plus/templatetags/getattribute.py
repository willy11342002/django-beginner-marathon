from django import template
register = template.Library()

def getattribute(value, arg):
    return getattr(value, arg)

register.filter('getattribute', getattribute)
