from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    """Recipe model."""
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='ingredients',
        related_name='recipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='tags',
        related_name='recipe',
        blank=True, )
    image = models.ImageField(
        'recipe photo',
        upload_to='static/recipe/',
        blank=True,
        null=True)
    name = models.CharField(
        'recipe name',
        max_length=200,
        blank=False)
    text = models.TextField(
        'recipe description',
        blank=False)
    cooking_time = models.PositiveSmallIntegerField(
        'cooking time')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='author')
    pub_date = models.DateTimeField(
        'creation date',
        auto_now_add=True)
    date_update = models.DateTimeField(
        'modifed date',
        auto_now=True)

    def get_ingredients(self):
        return [
            ingredient[
                'name'
            ] for ingredient in self.ingredients.values('name')]

    def get_tags(self):
        return [tag.get('name') for tag in self.tags.values('name')]

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.name} from {self.author.first_name}'


class RecipeIngredient(models.Model):
    """RecipeIngredient model."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient')
    amount = models.PositiveSmallIntegerField(
        'amount', )

    class Meta:
        verbose_name = 'ingredient quantity'
        verbose_name_plural = 'quantity of ingredients'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient')]


class FavoriteRecipe(models.Model):
    """FavoriteRecipe model."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='user',
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='favorite_recipe',
        verbose_name='recipe',
    )
    favorite_date = models.DateTimeField(
        'favorite date',
        auto_now_add=True)

    def get_recipe(self):
        return [
            recipe[
                'name'
            ] for recipe in self.recipes.values('name')
        ]

    @receiver(post_save, sender=User)
    def create_favorite_recipe(
            sender, instance, created, **kwargs):
        if created:
            return FavoriteRecipe.objects.create(user=instance)
        return None

    def __str__(self):
        return f'{self.user} favorite {self.recipes}'


class ShoppingCart(models.Model):
    """ShoppingCart model."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='user')
    recipes = models.ManyToManyField(
        Recipe,
        related_name='shopping_cart',
        verbose_name='recipe')

    def get_recipe(self):
        return [
            recipe['name'] for recipe in self.recipes.values('name')
        ]

    @receiver(post_save, sender=User)
    def create_shopping_cart(
            sender, instance, created, **kwargs):
        if created:
            return ShoppingCart.objects.create(user=instance)
        return None

    class Meta:
        verbose_name = 'purchase'
        verbose_name_plural = 'purchases'
        ordering = ['-id']

    def __str__(self):
        shopping_cart = [
            recipe['name'] for recipe in self.recipes.values('name')
        ]
        return f'{self.user} shopping cart: {shopping_cart}'
