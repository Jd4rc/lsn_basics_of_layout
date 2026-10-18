from django.core.cache import caches
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from catalog.models import Category, Product


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
