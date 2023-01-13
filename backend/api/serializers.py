from django.db import transaction
from rest_framework import serializers

from api.utils import Base64ImageField, validate_input_value
from recipes.models import (Favorite, Ingredient, IngredientAmountForRecipe,
                            Recipe, ShoppingCart, Tag)
from users.serializers import UserDetailSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientAmountForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmountForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserDetailSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date', )
        read_only_fields = (
            'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart'
        )

    def get_ingredients(self, obj):
        queryset = obj.ingredient_amount.all()
        return IngredientAmountForRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.favorite_recipe.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.recipe_in_cart.filter(recipe=obj).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountForRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, attrs):
        ingredients = self.initial_data.get('ingredients')
        validated_ingrediets = []
        unique_ingredients_id = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError({
                    'Ингредиент': (
                        'Не существующий ингредиент: {}'.format(ingredient_id)
                    )
                })

            if ingredient_id in unique_ingredients_id:
                raise serializers.ValidationError({
                    'Ингредиент': (
                        'Ингредиенты не должны повторяться.'
                    )
                })
            unique_ingredients_id.append(ingredient_id)

            amount = validate_input_value(
                int(ingredient.get('amount')),
                field_name='Ингредиент',
                error_message=(
                    'Количество ингредиента должно '
                    'быть больше или равно'
                )
            )

            validated_ingrediets.append(
                {'id': ingredient_id, 'amount': amount}
            )

        text_in_list: list[str] = list(self.initial_data.get('text'))
        text_in_list[0] = text_in_list[0].capitalize()
        text: str = ''.join(text_in_list)

        attrs['ingredients'] = validated_ingrediets
        attrs['name'] = str(self.initial_data.get('name')).capitalize()
        attrs['text'] = text

        return attrs

    def _set_amount_to_ingredient(self, recipe, ingredients):
        for ingredient in ingredients:
            IngredientAmountForRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

    @transaction.atomic
    def create(self, validated_data):
        validated_data['author'] = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self._set_amount_to_ingredient(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        recipe = instance

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            self._set_amount_to_ingredient(recipe, ingredients)

        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipesListSerializer(instance, context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, attrs):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        if user.favorite_recipe.filter(recipe=attrs.get('recipe')).exists():
            raise serializers.ValidationError(
                {'error': 'Данный рецепт уже добавлен в избранное.'}
            )
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, attrs):
        user = self.context.get('request').user
        # if not user.is_authenticated:
        #     return False
        if user.recipe_in_cart.filter(recipe=attrs.get('recipe')).exists():
            raise serializers.ValidationError(
                {'error': 'Данный рецепт уже добавлен в список покупок.'}
            )
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': request}
        ).data
