from django.core.cache import cache, caches
from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from catalog.models import Category, Product
from catalog.services import category_products_cache_key


@receiver([post_save, post_delete], sender=Product)
@receiver([post_save, post_delete], sender=Category)
def clear_product_pages_cache(sender, **kwargs):
    """Изменился товар или категория — закешированные страницы товаров устарели.

    Ключ cache_page — хеш адреса и заголовков, к товару его не привязать, поэтому
    чистится весь кеш 'pages'. Категория — потому что её название есть на странице
    товара и в меню. Счётчик просмотров меняется через update(), сигналов не шлёт
    и кеш не сбрасывает.
    """
    # После коммита: очисти раньше — соседний запрос успел бы закешировать старые данные
    transaction.on_commit(caches['pages'].clear)


@receiver(pre_save, sender=Product)
def remember_old_category(sender, instance, **kwargs):
    """Запоминает категорию товара до сохранения: в post_save в базе уже новая."""
    instance._old_category_id = (
        Product.objects.filter(pk=instance.pk).values_list('category_id', flat=True).first()
        if instance.pk else None
    )


@receiver([post_save, post_delete], sender=Product)
def clear_category_products_cache(sender, instance, **kwargs):
    """Товар изменился — список его категории устарел. Перенесли в другую — и старой тоже."""
    category_ids = {instance.category_id, getattr(instance, '_old_category_id', None)} - {None}
    keys = [category_products_cache_key(pk) for pk in category_ids]
    # Только свои ключи, не clear(): у Redis это FLUSHDB всей базы 'default'
    transaction.on_commit(lambda: cache.delete_many(keys))


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    """В закешированных товарах лежит и сама категория (название, описание)."""
    key = category_products_cache_key(instance.pk)
    transaction.on_commit(lambda: cache.delete(key))
