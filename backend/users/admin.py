from django.contrib import admin
from users.models import Follow, User


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Класс админки подписок."""
    list_display = ('author', 'user')
    list_filter = ('author', 'user')
    search_fields = ('author__username', 'user__username')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс админки пользователя."""
    list_display = ('username', 'email')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
