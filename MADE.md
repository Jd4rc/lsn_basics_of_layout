# Сделано

Короткий журнал. Что осталось — в `TODO.md`. Подробности изменений — в `git log`.

## CRUD для Product — закрыт

| Операция | Статус | Коммит |
|---|---|---|
| Create | ✅ | было до этой работы |
| Read (список + карточка) | ✅ | было до этой работы |
| Update | ✅ | `7b0bcab` |
| Delete | ✅ | `f0e18e9` |

---

## 2026-09-24 · `Product.get_absolute_url()` · `9eef2a5`

- `models.py` — `get_absolute_url()` → `reverse('catalog:product_detail', kwargs={'pk': self.pk})`

**Знать:** внутри метода — обычный `reverse`, не `reverse_lazy`: метод вызывается
во время запроса, когда URL-ы уже загружены. `reverse_lazy` нужен только там, где код
выполняется при импорте — атрибуты класса, константы модуля, аргументы декораторов.
Миграция не нужна: методы схему БД не трогают, `makemigrations --check` → `No changes detected`.

Что даёт сразу, без CBV:
- в админке на странице товара появилась кнопка View on site (`/admin/r/<ct>/<pk>/`) —
  Django показывает её сам, если у модели есть `get_absolute_url()`
- `redirect(product)` — `redirect` принимает модель и сам зовёт `get_absolute_url()`
- `{{ product.get_absolute_url }}` в шаблонах вместо `{% url 'catalog:product_detail' product.pk %}`
- на будущее: `CreateView` / `UpdateView` без `success_url` редиректят сюда сами

## 2026-09-24 · ContactForm и редирект на контактах · `0e10b8f`

- `forms.py` — `ContactForm(forms.Form)`: имя (≤100), телефон (≤20, `type="tel"`), сообщение.
  Все обязательные, ошибки по-русски прямо в `error_messages` — в `settings.py`
  `LANGUAGE_CODE = 'en-us'`, стандартные тексты были бы английскими
- `views.py` — `contacts` устроена как `product_create`: валидна → `messages.success` +
  `redirect('catalog:contacts')`, нет → `render` с ошибками
- `contacts.html` — `{% if sent %}` → цикл по `messages`; поля, написанные вручную, →
  цикл по `form` с `field.errors`, как в `product_form.html`; `novalidate` на форме
- `.gitignore` — `/CLAUDE.md` (заехал в этот же коммит)

**Знать:** после `redirect` контекст теряется — флаг `sent` до следующего GET
не доживёт. Поэтому сообщение идёт через `django.contrib.messages`: оно кладётся
в хранилище (cookie/сессия), показывается один раз и исчезает.
Атрибут `required` в HTML обходился через DevTools или `curl` — теперь проверка на сервере.

## 2026-09-23 · Delete для Product · `f0e18e9`

- `views.py` — `product_delete(request, pk)`: GET показывает подтверждение, POST удаляет + `redirect('catalog:home')`
- `urls.py` — путь `products/<int:pk>/delete/`
- `product_confirm_delete.html` — новый шаблон, кнопка внутри `<form method="post">` с `{% csrf_token %}`
- `product_detail.html` — кнопка «Удалить»

**Знать:** `product.delete()` удаляет строку в БД, но **не файл картинки** из `media/products/`.
Django специально так делает с версии 1.3 — на один файл могут ссылаться несколько записей.
Осиротевшие jpg копятся. Для учебного проекта нормально, на бою чистят сигналом `post_delete`.

## 2026-09-23 · Локальные заметки под игнор · `1663fb6`

`/TODO.md` и `/MADE.md` в `.gitignore`. Ведущий слэш = игнор только в корне.

## 2026-09-23 · Update для Product · `7b0bcab`

- `urls.py` — путь `products/<int:pk>/edit/`, выше `<slug:slug>/`
- `views.py` — `product_update(request, pk)`, `instance=product` в обе ветки
- `product_form.html` — заголовок и «Отмена» переключаются по `form.instance.pk`
- `product_detail.html` — кнопка «Редактировать»

**Грабли:** URL и вьюха должны ехать одним коммитом. `urls.py` читается целиком
при старте — путь на несуществующую вьюху роняет весь сайт, а не одну страницу.

---

## Что практически изменилось на сайте

Карточка товара из страницы для чтения стала рабочим местом: три кнопки вместо одной,
опечатки правятся без админки, товар удаляется с подтверждением.

Поле «Обновлён» наконец что-то значит — до Update оно всегда совпадало с «Добавлен»,
потому что `save()` вызывался ровно один раз в жизни объекта.

Форма контактов: F5 после отправки больше не дублирует сообщение, пустые поля
ловятся на сервере с ошибкой под каждым полем, а введённое при ошибке не пропадает.

В админке на странице товара — кнопка View on site: из правки товара
в один клик на его публичную карточку.
