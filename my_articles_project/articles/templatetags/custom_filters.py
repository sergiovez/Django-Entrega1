# articles/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, key):
    """
    Divide un string por el separador dado y devuelve una lista.
    """
    if value:
        return value.split(key)
    return []
