# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## О проекте

Учебный Django-проект (домашние задания `hw_NN`): витрина аквариумного магазина.
Python 3.14, Django 6.1, PostgreSQL через `psycopg`, зависимости в Poetry
(`package-mode = false`). Подробная документация по страницам, формам и моделям в
`README.md`.

`TODO.md` и `MADE.md` в корне — заметки пользователя: что осталось сделать
и журнал сделанного. Смотри их перед новой задачей.

## Команды

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py makemigrations catalog
poetry run python manage.py runserver

poetry run python manage.py load_fixture_catalog   # loaddata catalog_fixture.json
poetry run python manage.py delete_data_in_db      # удаляет Product и Category, ContactInfo и Feedback не трогает

# пересохранить фикстуру: только через -o, `>` в PowerShell ломает кодировку UTF-8
poetry run python manage.py dumpdata catalog --indent 2 -o catalog_fixture.json

poetry run python manage.py test catalog                                  # все тесты
poetry run python manage.py test catalog.tests.SomeTestCase.test_method   # один тест
```

- Тесты пока не написаны (`catalog/tests.py` пустой). Они идут на PostgreSQL, поэтому
  у пользователя из `DB_USER` должно быть право `CREATEDB` для тестовой базы.
- Линтера и форматтера в проекте нет.
- Без `.env` с `SECRET_KEY` ничего не запустится: `settings.py` читает его через
  `os.environ['SECRET_KEY']`. Оттуда же берутся `DEBUG` и `DB_*`. `ALLOWED_HOSTS`
  в `.env.example` есть, но настройки его не читают: список захардкожен в `settings.py`.
- Почта настроена через `MAILERS` (формат Django 6.1, не `EMAIL_*`). Без `EMAIL_HOST`
  в `.env` работает console backend: письма печатаются в консоль `runserver`, тема
  и тело — в base64.

## Архитектура

- `config/` — настройки проекта, `catalog/` — единственное приложение, в нём вся логика.
- Все вьюхи — generic CBV: `ProductListView`, `ProductDetailView`, `ProductCreateView`,
  `ProductUpdateView`, `ProductDeleteView`, `CategoryProductListView`, `FeedbackCreateView`.
  Новые пишем так же. Имена — `<Модель><Действие>View` (у формы без модели — по форме),
  шаблоны — по дефолтным именам Django (`<model>_detail.html`, `_form.html`,
  `_confirm_delete.html`), `template_name` задаём, только если имя другое.
- Грабли CBV: миксины (`LoginRequiredMixin`, `SuccessMessageMixin`, `NearestPageMixin`)
  ставятся левее базового класса, справа молча не работают. `success_url` в атрибуте
  класса — только `reverse_lazy` (атрибут вычисляется при импорте, URL-ы ещё не
  загружены), зависит от объекта — `get_success_url()`. Переопределённый `form_valid()`
  возвращает `super().form_valid(form)`, иначе ни сохранения, ни редиректа.
  `form_class` и `fields` вместе — `ImproperlyConfigured`.
- Списки с пагинацией — через `NearestPageMixin`: кривой `?page=` даёт ближайшую
  страницу, а не 404.
- После успешного POST — редирект (Post/Redirect/Get). `FeedbackCreateView` сообщает
  об отправке через `SuccessMessageMixin` (`django.contrib.messages`): после редиректа
  контекст теряется.
- `ProductCreateView` и `ProductUpdateView` используют один шаблон `product_form.html`
  (дефолтное имя у обоих), который различает режимы по `form.instance.pk`.
  Валидация `ProductForm` — в методах `clean_<поле>`, CSS-классы полей задаются
  в `Meta.widgets`.
- **Порядок в `catalog/urls.py` важен:** `<slug:slug>/` (страница категории)
  подходит под любой одиночный сегмент пути, поэтому стоит последним. Новые маршруты
  добавлять выше него.
- `catalog.context_processors.menu_categories` кладёт `menu_categories` в контекст
  каждого шаблона (меню в `nav.html`, плитки на главной). Вьюхам не нужно передавать
  категории самим.
- Шаблоны: общий макет `templates/base.html` (блоки `title`, `content`, `extra_css`,
  `extra_js`), общие куски в `templates/includes/` (`nav.html`; `pagination.html`
  ждёт `page_obj`), шаблоны приложения в `catalog/templates/catalog/`, карточка
  товара — `catalog/includes/product_card.html` (ждёт `product`).
- В списках показываются только товары с `is_active=True`, страница товара по прямой
  ссылке открывается всегда.
- Просмотры (`Product.views_count`) считает `ProductDetailView.get_object()` через
  `update()` с `F()`, а не `save()`: `save()` сдвинул бы `updated_at` (`auto_now`).
  Новое значение читается в той же транзакции, что и `UPDATE`: только так письмо
  на `VIEWS_MILESTONE` (`catalog/emails.py`) уходит ровно один раз при одновременных
  открытиях.
- `Product.category` — `on_delete=PROTECT`, `related_name='products'`: категорию
  с товарами удалить нельзя (`ProtectedError`), поэтому товары удаляются первыми.
- Загруженные фото лежат в `media/products/` (в `.gitignore`). Django раздаёт их
  только при `DEBUG=True`. `product.delete()` файл картинки не удаляет.
- Bootstrap 5 подключён локально из `static/`. Собственный стиль — классы
  `*-ink`, `tile`, `poster`, `credits`, `notice`, `field-error` в `static/css/style.css`.
  Для новых элементов бери их, а не голый Bootstrap.

## Соглашения

- Тексты интерфейса, `verbose_name`, сообщения валидации и комментарии пишем
  по-русски. Сообщения коммитов — по-английски, conventional commits (`feat:`,
  `fix:`, `refactor:`, `chore:`, `docs:`, `style:`, `data:`).
- Ветки `feature/hw_NN`, PR вливаются в `develop` (`main` отстаёт). В конце домашки
  README обновляется отдельным коммитом `docs: update README`.
- Каждый коммит оставляет проект рабочим: URL и его вьюха попадают в один коммит
  (`urls.py` загружается целиком при старте, и ссылка на несуществующую вьюху
  роняет весь сайт). Один коммит — одна причина изменения. Новые файлы добавляются
  явным `git add`.
- Коммитит пользователь сам: не запускай `git add` и `git commit`. Вместо этого
  предложи, как разбить изменения на коммиты, и сообщения к ним по правилам выше.
- После задачи, которая меняет код или настройки, в том же ответе обнови заметки:
  в `TODO.md` убери закрытые пункты и поправь затронутые (номера строк, зависимости),
  в `MADE.md` добавь запись на 2–4 строки, блок «Знать» — только если были грабли.
  Коммит в записи указывай предложенным сообщением (`refactor: ...`), не хэшем —
  заметки едут в том же коммите, что и код. Вопросы и объяснения заметки не трогают.
  В итоговом ответе одна строка: что обновлено в заметках или почему нет.
