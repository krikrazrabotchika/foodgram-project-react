from __future__ import annotations

import base64

from django.core.files.base import ContentFile
from django.utils.timezone import datetime
from rest_framework.serializers import ImageField, ValidationError

from api.conf import LIMIT_VALUE


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def get_shopping_cart_footer() -> str:
    time_format_message: str = 'Список создан в %H:%M от %d/%m/%Y'
    separate: str = '-' * len(time_format_message)
    return separate + '\n' + datetime.now().strftime(time_format_message)


def validate_input_value(
    value: int,
    field_name: str,
    error_message: str,
    limit_value: int = LIMIT_VALUE
) -> str | int:
    if value < limit_value:
        raise ValidationError({
            field_name: '{} {}.'.format(error_message, limit_value)
        })
    return value
