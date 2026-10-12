from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users.managers import UserManager

phone_validator = RegexValidator(
    r'^\+?\d{10,15}$',
    'Номер — от 10 до 15 цифр, можно с «+» в начале, например +375291234567.',
)


class User(AbstractUser):
    """Пользователь магазина. Входит по email, username нет."""

    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(
        upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар'
    )
    phone_number = models.CharField(
        max_length=16, blank=True, validators=[phone_validator], verbose_name='Номер телефона'
    )
    country = models.CharField(max_length=50, blank=True, verbose_name='Страна')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # email и пароль createsuperuser спросит и так

    objects = UserManager()

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.email
