from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Загружает данные из фикстуры"

    def handle(self, *args, **options):
        call_command('loaddata', 'catalog_fixture.json')
        self.stdout.write('Successfully loaded')
