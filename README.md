# lsn_basics_of_layout

Учебный Django-проект: витрина магазина аквариумов, рыбок, растений и сопутствующего
оборудования. Есть вёрстка на шаблонах Django с наследованием от общего макета и
формой обратной связи, а также слой данных: категории и товары, хранящиеся в
PostgreSQL, и контактная информация магазина, редактируемая через админку.

## Стек

- Python 3.14
- Django 6.1
- Bootstrap 5 (подключён локально из `static/`)
- PostgreSQL (доступ через `psycopg`)
- python-dotenv — переменные окружения из `.env`
- Poetry — управление зависимостями

## Установка

```bash
git clone https://github.com/Jd4rc/lsn_basics_of_layout.git
cd lsn_basics_of_layout
poetry install
```

Создать файл `.env` в корне проекта с настройками подключения к PostgreSQL:

```
SECRET_KEY=django-insecure-...
DEBUG=True
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=5432
```

Применить миграции и запустить сервер:

```bash
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Если виртуальное окружение уже активировано, префикс `poetry run` можно опускать.

## Страницы

| URL | Метод | Имя маршрута | Шаблон |
|---|---|---|---|
| `/catalog/` | GET | `catalog:home` | `catalog/home.html` |
| `/catalog/contacts/` | GET, POST | `catalog:contacts` | `catalog/contacts.html` |
| `/catalog/<slug>/` | GET | `catalog:category_detail` | `catalog/category_detail.html` |
| `/admin/` | — | — | админка Django |

## Структура

```
lsn_basics_of_layout/
├── catalog/                     # основное приложение
│   ├── templates/catalog/       # шаблоны приложения
│   │   ├── home.html
│   │   ├── contacts.html
│   │   └── category_detail.html
│   ├── management/commands/     # кастомные management-команды
│   │   ├── load_fixture_catalog.py
│   │   └── delete_data_in_db.py
│   ├── migrations/
│   ├── models.py
│   ├── admin.py
│   ├── urls.py
│   └── views.py
├── config/                      # настройки проекта
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── static/
│   ├── css/                     # bootstrap.min.css, style.css
│   ├── js/                      # bootstrap.bundle.min.js
│   └── images/                  # fish.svg, ferb.jpg
├── templates/
│   └── base.html                # общий макет проекта
├── manage.py
└── pyproject.toml
```

### Шаблоны

`templates/base.html` в корне проекта — общий макет: шапка с навигацией, подвал,
подключение стилей и скриптов. Страницы приложения наследуются от него через
`{% extends 'base.html' %}` и переопределяют блоки `title` и `content`.

Шаблоны самого приложения лежат в `catalog/templates/catalog/` — вложенная папка
с именем приложения нужна, чтобы имена не конфликтовали с шаблонами других
приложений.

### Модели

- **`Category`** — категория товаров (`name`, `description`, `slug`).
- **`Product`** — товар: `ForeignKey` на `Category` (`on_delete=PROTECT`,
  `related_name='products'`), цена, остаток на складе, состояние (новый, б/у),
  флаг «в продаже», фото, даты создания и обновления.
- **`ContactInfo`** — контактные данные магазина (телефон, email, адрес, часы
  работы), заполняются через админку и выводятся на странице контактов.

### Management-команды

- `python manage.py load_fixture_catalog` — загружает тестовые данные каталога
  из фикстуры.
- `python manage.py delete_data_in_db` — очищает данные каталога из базы.

### Форма обратной связи

На странице контактов есть форма с полями «имя», «телефон» и «сообщение».
POST-запрос обрабатывается во вьюхе `catalog.views.contacts`: данные читаются
из `request.POST`, выводятся в консоль сервера, после чего страница
перерисовывается с сообщением об успешной отправке. Это отдельно от блока
контактной информации на той же странице — тот берётся из модели `ContactInfo`
и не связан с отправленной формой.

Форма защищена CSRF-токеном (`{% csrf_token %}` в шаблоне). При отправке запроса
в обход браузера — например, через Postman — нужно сначала выполнить GET, чтобы
получить cookie `csrftoken`, а затем передать её значение в поле
`csrfmiddlewaretoken` или в заголовке `X-CSRFToken`. Иначе Django вернёт
403 с текстом «CSRF verification failed».

Хранение отправленных сообщений в базе и валидация через `forms.Form` пока не
реализованы.

### Оформление

Собственные стили — в `static/css/style.css`. Визуальная идея взята с киноафиши:
пыльно-розовый фон, крупные серифные заголовки, подписи узким гротеском в верхнем
регистре, чёрные рамки без скруглений и SVG-зерно поверх страницы.

## Лицензия

MIT — см. файл [LICENSE](LICENSE).
