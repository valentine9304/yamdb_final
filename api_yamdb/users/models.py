from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'
ROLES = [
    (USER, 'user'),
    (ADMIN, 'admin'),
    (MODERATOR, 'moderator')
]


class User(AbstractUser):
    """Кастомизированная модель Пользователей."""

    username = models.CharField(
        max_length=150,
        verbose_name='Логин',
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'^[\w@.+-_]+$',
            message='Недопустимые символы.'
        )]
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='E-mail',
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )
    role = models.CharField(
        max_length=20,
        verbose_name='Роль',
        choices=ROLES,
        default="user"
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)
