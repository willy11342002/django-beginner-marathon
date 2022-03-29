from django import template
register = template.Library()

def getitems(value, arg):
    return value.get(arg)

register.filter('getitems', getitems)
