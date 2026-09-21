from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def percentage(value, total):
    if total > 0:
        return (value / total) * 100
    return 0