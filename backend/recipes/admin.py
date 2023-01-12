from django.contrib import admin

from .models import FavoriteRecipe, Recipe, RecipeIngredient, ShoppingCart


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'get_favorite_count',
        'text',
        'cooking_time',
        'get_tags',
        'image',
        'pub_date',
        'date_update',
        )
    inlines = (RecipeIngredientAdmin,)
    search_fields = (
        'author__email',
        'name',
        'text',
        'ingredients__name',
        'cooking_time',
        'tags__name',
        'pub_date',
        'date_update',
        )
    list_filter = (
        'author',
        'ingredients',
        'cooking_time',
        'tags',
        'pub_date',
        'date_update',
        )
    empty_value_display = '-empty-'

    @admin.display(description='In favorite')
    def get_favorite_count(self, obj):
        return obj.favorite_recipe.count()

    @admin.display(description='Recipe tags')
    def get_tags(self, obj):
        return obj.get_tags()


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
        'favorite_date',
        )
    search_fields = (
        'user__email',
        'recipes__name',
        'favorite_date',
        )
    list_filter = (
        'user__email',
        'recipes__name',
        'favorite_date',
        )
    empty_value_display = '-empty-'

    @admin.display(description='recipe')
    def recipe(self, obj):
        return obj.get_recipe()
    empty_value_display = '-empty-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
        )
    search_fields = (
        'user__email',
        'recipes__name',
        )
    list_filter = (
        'user__email',
        'recipes__name',
        )
    empty_value_display = '-empty-'

    @admin.display(description='recipe')
    def recipe(self, obj):
        return obj.get_recipe()
    empty_value_display = '-empty-'
