from django import template

register = template.Library()


@register.filter
def index(sequence, position):
    return sequence[position]


@register.filter
def multiply(value, arg):
    return value * arg
