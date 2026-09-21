from catalog.models import Category


def menu_categories(request):
    """Категории для главного меню, доступны в любом шаблоне."""
    return {'menu_categories': Category.objects.all()}
