from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

# Группа → права в формате <app_label>.<codename>
GROUPS = {
    'Модератор продуктов': (
        'catalog.can_unpublish_product',
        'catalog.delete_product',
        'catalog.change_product',
    ),
}


class Command(BaseCommand):
    help = 'Создаёт группы пользователей и выдаёт им права. Запускать после migrate, можно повторно'

    def handle(self, *args, **options):
        for name, perm_names in GROUPS.items():
            permissions = []
            for perm_name in perm_names:
                app_label, codename = perm_name.split('.')
                try:
                    permissions.append(
                        Permission.objects.get(content_type__app_label=app_label, codename=codename)
                    )
                except Permission.DoesNotExist:
                    # Права создаёт migrate (сигнал post_migrate), а не makemigrations
                    raise CommandError(f'Нет права {perm_name}. Сначала выполните migrate.')

            group, created = Group.objects.get_or_create(name=name)
            # set, а не add: повторный запуск приводит права группы ровно к списку выше
            group.permissions.set(permissions)
            status = 'создана' if created else 'обновлена'
            self.stdout.write(self.style.SUCCESS(f'Группа «{name}» {status}: {", ".join(perm_names)}'))
