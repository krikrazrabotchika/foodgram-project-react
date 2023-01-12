from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredient, ShoppingCart
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from tags.models import Tag
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeSubscribeSerializer, RecipeWriteSerializer,
                          SubscribeSerializer, TagSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """User ViewSet."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientTagViewSet(viewsets.ModelViewSet):
    """Ingredient and Tag mixin ViewSet."""
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientFilter, )
    filterset_fields = ('name',)
    search_fields = ('name',)
    ordering_fields = ('name',)


class IngredientViewSet(IngredientTagViewSet):
    """Ingredient ViewSet."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(IngredientTagViewSet):
    """Tag mixin ViewSet."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Recipe ViewSet."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'Recipe deleted successfully.'
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({
                'The wind blows from the void.'
            }, status=status.HTTP_400_BAD_REQUEST)


class GetObjectMixin(
        generics.CreateAPIView,
        generics.DestroyAPIView):
    """AddDeleteFavoriteRecipe and AddDeleteShoppingCart mixin ViewSet."""

    serializer_class = RecipeSubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe


class AddDeleteFavoriteRecipe(GetObjectMixin):
    """AddDeleteFavoriteRecipe ViewSet."""

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.favorite_recipe.recipes.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.favorite_recipe.recipes.remove(instance)
        return Response(
            {'Recipe removed from favorites.'},
            status=status.HTTP_204_NO_CONTENT)


class AddDeleteShoppingCart(GetObjectMixin):
    """AddDeleteShoppingCart ViewSet."""

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.shopping_cart.recipes.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.shopping_cart.recipes.remove(instance)
        return Response(
            {'Recipe removed from shoping cart.'},
            status=status.HTTP_204_NO_CONTENT)


class AddAndDeleteSubscribe(
        generics.DestroyAPIView,
        generics.CreateAPIView,
        generics.ListAPIView):
    """AddAndDeleteSubscribe ViewSet."""

    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.follower.all()

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def get_id(self):
        return self.kwargs['user_id']

    def perform_create(self, serializer):
        instance = self.get_object()
        id = self.get_id()
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=self.request.user,
            author=instance,
            id=id
        )

    def perform_destroy(self, instance):
        self.request.user.follower.filter(author=instance).delete()


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, ))
def download_shopping_cart(request):
    """
    Схема работы для метода пост запроса:
    Пользователь передает свой чат айди
    {
        "chat_id": "123456789"
    }
    Бот отправляет ему список покупок.
    """

    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).order_by('ingredient__name').values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))

    recipes_list = ShoppingCart.objects.filter(
        user=request.user
    ).values(
        'recipes__name'
    )
    shopping_list = ('Для приготовления следующих блюд:')
    recipe_name = 'recipes__name'
    ingredient_name = 'ingredient__name'
    unit = 'ingredient__measurement_unit'
    amount = 'amount'

    for recipe in recipes_list:
        shopping_list += (f'\n - {recipe[recipe_name]}')

    shopping_list += ('\nВ общей сложности необходимо преобрести:')

    for count, _ in enumerate(ingredients, start=1):
        shopping_list += (
            f'\n{count}) {_[ingredient_name]} - {_[amount]} {_[unit]}')
    file = 'shopping_list.txt'
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
    if request.method == 'GET':
        return response
