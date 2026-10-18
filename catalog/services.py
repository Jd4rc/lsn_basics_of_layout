from catalog.models import Product


def get_published_products_by_category(category):
    """Опубликованные товары категории — то, что видит посетитель на её странице.

    Через category.products, а не Product.objects.filter(category=...): связанный менеджер
    сразу подставляет товарам эту категорию, и product.category не идёт в базу за каждым.
    """
    return category.products.filter(is_published=True)
