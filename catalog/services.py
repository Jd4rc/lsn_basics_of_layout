from django.core.cache import cache

CATEGORY_PRODUCTS_CACHE_TIMEOUT = 60 * 15


def category_products_cache_key(category_id):
    """Ключ кеша товаров категории. Им же пользуется сброс в catalog/signals.py."""
    return f'category_{category_id}'


def get_published_products_by_category(category):
    """Опубликованные товары категории — то, что видит посетитель на её странице.

    Список лежит в кеше 'default' под ключом category_<id>. Через category.products,
    а не Product.objects.filter(category=...): связанный менеджер сразу подставляет
    товарам эту категорию, и product.category не идёт в базу за каждым.
    """
    key = category_products_cache_key(category.pk)
    products = cache.get(key)
    # is None, а не not: пустая категория ([]) тоже берётся из кеша, а не из базы
    if products is None:
        # list(): QuerySet ленивый, в кеш попал бы запрос, а не товары
        products = list(category.products.filter(is_published=True))
        cache.set(key, products, CATEGORY_PRODUCTS_CACHE_TIMEOUT)
    return products
