from django import template
from django.utils.text import slugify

register = template.Library()

@register.filter
def urlify(value):
    return '_'.join(word.capitalize() for word in value.split(' '))


