import datetime
from django import template

register = template.Library()

@register.filter 
def mul(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''
    
@register.filter
def format_date(value):
    if isinstance(value, datetime.date):
        return value.strftime('%d/%m/%Y')
    return value