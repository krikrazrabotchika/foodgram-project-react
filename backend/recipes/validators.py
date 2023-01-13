import re

from django.core.exceptions import ValidationError


def validate_color(value):
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value)
    if not match:
        raise ValidationError('Цвет должен быть в виде HEX-кода.')
    return value
