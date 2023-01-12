from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, serializers
from drf_base64.fields import Base64ImageField
from ingredients.models import Ingredient
from recipes.models import (FavoriteRecipe, Recipe, RecipeIngredient,
                            ShoppingCart)
from tags.models import Tag
from users.models import Subscribe, User


class UserSerializer(UserSerializer):
    """User Model Serializer."""
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.follower.filter(
            author=obj
        ).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient Model Serializer."""

    class Meta:
        fields = ('id', 'name', 'measurement_unit',)
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Tag Model Serializer."""

    class Meta:
        fields = ('id', 'name', 'color', 'slug',)
        model = Tag


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Recipe Ingredient Read Model Serializer."""
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Recipe Model Read Serializer."""
    ingredients = RecipeIngredientReadSerializer(many=True, source='recipe')
    tags = TagSerializer(many=True)
    author = UserSerializer()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and FavoriteRecipe.objects.filter(
            user=user, recipes=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and ShoppingCart.objects.filter(
            user=user, recipes=obj
        ).exists()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Recipe Ingredient Write Model Serializer."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Recipe Model POST PATCH DELETE Serializer."""
    image = Base64ImageField(
        max_length=None,
        use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    ingredients = RecipeIngredientWriteSerializer(
        many=True)
    name = serializers.CharField(max_length=200)

    def validate(self, data):
        ingredients = data.get('ingredients')
        ingredient_list = []
        for items in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=items.get('id'))
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    f'A recipe cannot have the same ingredients. {ingredient}')
            ingredient_list.append(ingredient)
        tags = data.get('tags')
        tag_list = []
        if not tags:
            raise serializers.ValidationError(
                'Recipe must contain at least one tag.')
        for item in tags:
            tag = get_object_or_404(
                Tag, id=item.id)
            if tag in tag_list:
                raise serializers.ValidationError(
                    f'A recipe cannot have the same tags.'
                    f' {tag.id} > duplicated.')
            tag_list.append(tag)
        return data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Cooking time must not be less than one minute.')
        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Recipe must contain at least one ingredient.')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'The number of ingredients must be >= 1.')
        return ingredients

    @transaction.atomic
    def __create_ingredients(self, ingredients, recipe):
        recipeingredient_list = []
        for ingredient in ingredients:
            recipeingredient = RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
            recipeingredient_list.append(recipeingredient)
            self.RecipeIngredient = RecipeIngredient.objects.bulk_create(
                recipeingredient_list
            )

    @transaction.atomic
    def create(self, validated_data):
        if ('ingredients'
            and 'tags'
            and 'image'
            and 'name'
            and 'text'
                and 'cooking_time') in validated_data:
            image = validated_data.pop('image')
            ingredients = validated_data.pop('ingredients')
            tags = validated_data.pop('tags')
            recipe = Recipe.objects.create(image=image, **validated_data)
            recipe.tags.set(tags)
            self.__create_ingredients(ingredients, recipe)
            return recipe
        raise serializers.ValidationError(
            'All fields are required.')

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.__create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data

    class Meta:
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        model = Recipe
        read_only_fields = ('author',)
        extra_kwargs = {
            'ingredients': {'required': True},
            'tags': {'required': True},
            'image': {'required': True},
            'name': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True},
        }


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """Recipe Subscribe Serializer."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Author Subscribe Serializer."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.IntegerField(source='author.id', required=False)
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(method_name='_get_recipes')
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and Subscribe.objects.filter(
            user=user, author=obj.author
        ).exists()

    def _get_recipes(self, obj):
        request = self.context.get('request').data
        limit = request.get('recipes_limit')
        recipes = (
            obj.author.recipe.all()[:int(limit)] if limit
            else obj.author.recipe.all())
        return RecipeSubscribeSerializer(
            recipes,
            many=True).data

    def get_recipes_count(self, obj):
        author = obj.author
        return author.recipe.filter(author=obj.author).count()

    def validate(self, data):
        user = self.context.get('request').user
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('user_id')
        print(author_id)
        author = get_object_or_404(User, pk=author_id)
        if user == author:
            raise serializers.ValidationError(
                'You cannot subscribe to yourself.')
        if Subscribe.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'You are already subscribed to this author.')
        return data

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')
