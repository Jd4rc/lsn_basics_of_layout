from django.db import migrations, models


class Migration(migrations.Migration):
    # Написана руками: без вопроса «Did you rename...?» makemigrations сделал бы
    # RemoveField + AddField и потерял бы значения у уже существующих товаров

    dependencies = [
        ('catalog', '0006_feedback'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='is_active',
            new_name='is_published',
        ),
        migrations.AlterField(
            model_name='product',
            name='is_published',
            field=models.BooleanField(default=False, verbose_name='Опубликован'),
        ),
    ]
