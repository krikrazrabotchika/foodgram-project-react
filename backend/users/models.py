from api.conf import (
    ERROR_MESSAGE_FOR_VALIDATE_REGEX_USERNAME,
    REGEX_FOR_USERNAME
)
from django.contrib.auth.models import (
    AbstractUser, BaseUserManager
)
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Класс менджера пользователя."""
    def _create_user(
        self,
        first_name, last_name,
        username, email, password, **extra_fields
    ):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        first_name, last_name,
        username, email, password
    ):
        return self._create_user(
            first_name, last_name, username, email, password
        )

    def create_superuser(
        self,
        first_name, last_name,
        username, email, password
    ):
        return self._create_user(
            first_name, last_name,
            username, email, password,
            is_staff=True, is_superuser=True
        )


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[
            RegexValidator(
                regex=REGEX_FOR_USERNAME,
                message=_(ERROR_MESSAGE_FOR_VALIDATE_REGEX_USERNAME)
            )
        ]
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты',
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user'
            )
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follower'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            'Автор: [ {} ]; '
            'Подписчик: [ {} ]'
            .format(self.author, self.user)
        )
