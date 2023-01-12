from django.contrib import admin

from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'colored_color',
        'slug',
    )
    search_fields = (
        'name',
        'color',
        'slug',
    )

    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = '-empty-'
