from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL-имя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']

class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Категория',
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Цена, ₽'
    )
    stock = models.PositiveIntegerField(default=0, verbose_name='Остаток на складе')
    is_active = models.BooleanField(default=True, verbose_name='В продаже')
    image = models.ImageField(
        upload_to='products/', blank=True, null=True, verbose_name='Фото'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    def __str__(self):
        return f'{self.name} ({self.category})'

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ['-created_at', 'name']