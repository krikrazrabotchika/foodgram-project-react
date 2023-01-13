from django_filters import rest_framework as filters
from recipes.models import Recipe
from rest_framework.filters import SearchFilter


class IngredientSearchFilter(SearchFilter):
    """
    Добавляет возможность поиска ингредиента
    по названию, при создании рецепта.
    """
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтр для рецептов."""
    author = filters.CharFilter(
        field_name='author',
        method='get_filter_field'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='get_filter_field'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='get_filter_field'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_filter_field(self, queryset, name, value):
        if not value:  # and not self.request.user.is_authenticated:
            return queryset
        if name == 'is_favorited':
            return queryset.filter(
                favorite__user=self.request.user
            )
        if name == 'is_in_shopping_cart':
            return queryset.filter(
                shoppingcart__user=self.request.user
            )
        if name == 'author' and value == 'me':
            return queryset.filter(
                author=self.request.user
            )
        else:
            return queryset.filter(
                author__id=value
            )
