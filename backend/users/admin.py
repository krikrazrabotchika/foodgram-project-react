from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscribe

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name',
        )
    list_filter = (
        'first_name',
        'last_name',
        )
    empty_value_display = '-empty-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author',
        'subscribe_date',
        )
    search_fields = (
        'user__email',
        'author__email',
        )

    @admin.display(description='author')
    def author(self, obj):
        return obj.get_author()
    empty_value_display = '-empty-'
