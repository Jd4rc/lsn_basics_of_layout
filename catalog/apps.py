from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = 'catalog'

    def ready(self):
        # Регистрирует обработчики сигналов: сброс кеша страниц товаров
        from catalog import signals  # noqa: F401
