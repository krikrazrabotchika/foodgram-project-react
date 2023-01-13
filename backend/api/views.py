from django.db import transaction
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, response, serializers, status, viewsets
from rest_framework.decorators import action

from api.filters import IngredientSearchFilter, RecipeFilter
from api.paginations import CustomPagination
from api.permissions import IsAuthorAdminOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientAmountForRecipe,
                             IngredientSerializer, RecipeSerializer,
                             RecipesListSerializer, ShoppingCartSerializer,
                             TagSerializer)
from api.utils import get_shopping_cart_footer
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('$name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipesListSerializer
        return RecipeSerializer

    @transaction.atomic
    def _create_action(self, request, pk, serializer):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def _delete_action(self, request, pk, klass):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = get_object_or_404(klass=klass, user=user, recipe=recipe)
        obj.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST'], detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self._create_action(
            request=request, pk=pk, serializer=FavoriteSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self._delete_action(request=request, pk=pk, klass=Favorite)

    @action(
        methods=['POST'], detail=True,
        permission_classes=[permissions.AllowAny]
    )
    def shopping_cart(self, request, pk):
        return self._create_action(
            request=request, pk=pk, serializer=ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self._delete_action(
            request=request, pk=pk, klass=ShoppingCart
        )

    @action(
        methods=['GET'], detail=False,
        permission_classes=[permissions.AllowAny]
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.recipe_in_cart.exists():
            raise serializers.ValidationError({
                'error': 'В списке покупок нет ни одного рецепта.'
            })

        recipe_id_list = user.recipe_in_cart.values_list('recipe_id')
        ingredients_in_cart = IngredientAmountForRecipe.objects.filter(
            recipe__in=recipe_id_list
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount'
        )

        ingredients = {}
        for (name, measurement_unit, amount) in ingredients_in_cart:
            if name not in ingredients:
                ingredients[name] = {
                    'name': name,
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                ingredients[name]['amount'] += amount

        shopping_cart_out = 'Ваш список покупок:\n'
        for ingredient in ingredients.values():
            shopping_cart_out += '\u00B7 {} ({}) \u2014 {}\n'.format(
                ingredient['name'].capitalize(),
                ingredient['measurement_unit'],
                ingredient['amount']
            )
        shopping_cart_out += get_shopping_cart_footer()

        response = HttpResponse(
            shopping_cart_out, content_type='text/plain; charset=utf-8'
        )

        filename = str(user) + '-shopping-list' + '.txt'
        response['Content-Disposition'] = (
            'attachment; filename={}'.format(filename)
        )
        return response
