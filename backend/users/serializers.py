from djoser.serializers import UserCreateSerializer, UserSerializer
from foodgram.settings import RESERVED_USERNAME_LIST
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User


class UserDetailSerializer(UserSerializer):
    """
    Переопределяем сериализатор для пользователя.
    Добавлено поле подписки, если имеется подписчики.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.follower.filter(author=obj).exists()
            if user.is_authenticated else False
        )


class UserRegistrationSerializer(UserCreateSerializer):
    """
    Переопределяем регистрацию пользователя.
    Валидация по уникальности username и email.
    Валидация создания пользователя с username,
    который находится в зарезервированном списке.
    """

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email'],
            )
        ]

    def validate_username(self, value):
        if value.lower() in RESERVED_USERNAME_LIST:
            raise serializers.ValidationError(
                'Данное имя зарезервированно!'
            )
        return value


class FollowSerializer(UserDetailSerializer):
    """
    Сериализатор для подписок.
    Валидация по подписке на самого себя.
    Валидация по повторной подписке на автора.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('recipes', 'recipes_count')

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author',)
            )
        ]

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(recipes, many=True).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рецепта с меньшим кол-вом полей.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
