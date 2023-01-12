from django.urls import include, path
from rest_framework import routers

from .views import (AddAndDeleteSubscribe, AddDeleteFavoriteRecipe,
                    AddDeleteShoppingCart, IngredientViewSet, RecipeViewSet,
                    TagViewSet, download_shopping_cart)

app_name = 'api'

users_special_patterns = [
    path(
        '<int:user_id>/subscribe/',
        AddAndDeleteSubscribe.as_view(), name='subscribe'),
    path(
        'subscriptions/',
        AddAndDeleteSubscribe.as_view(), name='subscribe'),
]

recipes_special_patterns = [
    path(
        '<int:recipe_id>/favorite/',
        AddDeleteFavoriteRecipe.as_view(), name='favorite_recipe'),
    path(
        '<int:recipe_id>/shopping_cart/',
        AddDeleteShoppingCart.as_view(), name='shopping_cart'),
    path('download_shopping_cart/', download_shopping_cart),
]

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('users/', include(users_special_patterns)),
    path('recipes/', include(recipes_special_patterns)),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
