from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model."""
    email = models.EmailField(
        'email',
        max_length=200,
        unique=True, )
    first_name = models.CharField(
        'name',
        max_length=150)
    last_name = models.CharField(
        'surname',
        max_length=150)
    text = models.TextField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('id',)

    def __str__(self):
        return self.email


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='author',
        null=True,
    )
    subscribe_date = models.DateTimeField(
        'subscribe date',
        auto_now_add=True,
        null=True,
    )

    class Meta:
        verbose_name = 'subscribe'
        verbose_name_plural = 'subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription')]

    def get_author(self):
        # authors_list = [
        #     single_author[
        #         'email'
        #         ] for single_author in self.author.values('email')]
        return [single_author[
                    'email'
        ] for single_author in self.author.values('email')]

    def __str__(self):
        return f'{self.user} subscibed to {self.author}'
