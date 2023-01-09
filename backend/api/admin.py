from django.contrib import admin

from .models import Cart, Favorite, Ingredient, Recipe, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class IngredientsRecipesInline(admin.TabularInline):
    model = Recipe


class RecipesTagsInline(admin.TabularInline):
    model = Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags')
    inlines = [IngredientsRecipesInline, RecipesTagsInline]

    def count_favorites(self, obj):
        return obj.favorites.count()


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
