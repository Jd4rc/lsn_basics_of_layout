# lsn_basics_of_layout

Учебный Django-проект: витрина магазина аквариумов, рыбок, растений и сопутствующего
оборудования. Текущая версия — статическая вёрстка на шаблонах Django с наследованием
от общего макета. Моделей и работы с базой пока нет.

## Стек

- Python 3.14
- Django 6.1
- Bootstrap 5 (подключён локально из `static/`)
- SQLite
- Poetry — управление зависимостями

## Установка

```bash
git clone https://github.com/Jd4rc/lsn_basics_of_layout.git
cd lsn_basics_of_layout
poetry install
```

Применить миграции и запустить сервер:

```bash
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Если виртуальное окружение уже активировано, префикс `poetry run` можно опускать.

## Страницы

| URL | Имя маршрута | Шаблон |
|---|---|---|
| `/catalog/` | `catalog:home` | `catalog/home.html` |
| `/catalog/contacts/` | `catalog:contacts` | `catalog/contacts.html` |
| `/admin/` | — | админка Django |

## Структура

```
lsn_basics_of_layout/
├── catalog/                     # основное приложение
│   ├── templates/catalog/       # шаблоны приложения
│   │   ├── home.html
│   │   └── contacts.html
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
├── app.py                       # сервер на http.server из прошлого задания
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

### Оформление

Собственные стили — в `static/css/style.css`. Визуальная идея взята с киноафиши:
пыльно-розовый фон, крупные серифные заголовки, подписи узким гротеском в верхнем
регистре, чёрные рамки без скруглений и SVG-зерно поверх страницы.

## Лицензия

MIT — см. файл [LICENSE](LICENSE).
