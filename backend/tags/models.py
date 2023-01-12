from django.contrib import admin
from django.core.validators import RegexValidator
from django.db import models
from django.utils.html import format_html


class Tag(models.Model):
    """
        Tag model.
        COLOR_EXAMPLES = [
            ('#FF0000', 'RED'),
            ('#FF8000', 'ORANGE'),
            ('#FFFF00', 'YELLOW'),
            ('#80FF00', 'GREEN'),
            ('#00FFFF', 'LIGHT_BLUE'),
            ('#0080FF', 'BLUE'),
            ('#7F00FF', 'EPIC'),
            ('#FF00FF', 'PINK'),
            ('#FF007F', 'CORAL'),
        ]
    """

    name = models.CharField(
        'tag name',
        max_length=60,
        validators=[RegexValidator(
            r'^[A-Za-zА-Яа-яЁё\s]+$',
            message='The tag name can only contain letters and spaces'
            )],
        unique=True)
    color = models.CharField(
        'HEX tag color',
        max_length=7,
        validators=[RegexValidator(
            r'#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{6})$',
            message=(
                'A hex triplet is a six-digit, '
                'three-byte hexadecimal number. '
                'EXAMPLE --> #FF0000')
            )],
        unique=True)
    slug = models.SlugField(
        'link',
        max_length=100,
        unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['-id']

    def __str__(self):
        return self.name

    @admin.display(ordering='name')
    def colored_color(self):
        return format_html(
            f'<span style="color: {self.color};">{self.color}</span>'
        )
