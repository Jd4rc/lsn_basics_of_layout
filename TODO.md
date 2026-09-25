# TODO

Только то, что **осталось**. Сделанное — в `MADE.md`.

Легенда: ✅ готово · 🔒 только через админку

---

## Где мы сейчас

**CRUD для `Product` закрыт полностью и уже на классах (CBV).** Все три модели есть в `catalog/admin.py`,
так что у персонала CRUD полный и по остальным.

| Модель | Create | Read | Update | Delete |
|---|---|---|---|---|
| **Product** | ✅ | ✅ | ✅ | ✅ |
| **Category** | 🔒 | ✅ | 🔒 | 🔒 |
| **ContactInfo** | 🔒 | ✅ | 🔒 | 🔒 |

---

## 1. Права доступа ← стало блокирующим

Раньше это лежало в «отложено». После появления Delete — нет.

Сейчас **любой анонимный посетитель** может зайти на `/products/5/delete/`
и стереть товар. Безвозвратно, без логина. Ссылка «Удалить» висит в карточке
у всех на виду, искать не надо. Раньше он мог максимум насорить через
«Добавить товар» — теперь может удалять чужое.

- [ ] Закрыть `ProductCreateView`, `ProductUpdateView`, `ProductDeleteView` через
      `LoginRequiredMixin` — **левее** базового класса (вьюхи уже на CBV, `@login_required` не нужен)
- [ ] Убрать «Добавить товар» из `nav.html:20` для неавторизованных (`{% if user.is_authenticated %}`)
- [ ] Спрятать «Редактировать» и «Удалить» в `product_detail.html` тем же условием
- [ ] Настроить `LOGIN_URL` в `settings.py`, иначе редирект пойдёт на несуществующий `/accounts/login/`
- [ ] → `feat: restrict product management to logged-in users`

> Пока проект крутится на `runserver` у тебя на машине — не горит.
> В момент, когда окажется доступен откуда-то ещё, это дыра.
> Прятать кнопки в шаблоне **недостаточно** — адрес всё равно открывается напрямую.
> Защита на вьюхе обязательна, шаблон только про удобство.

---

## 2. Отдельные правки

Разные причины изменения — разные коммиты.

- [ ] **`print` в `contacts`.** `views.py:19` — отладочный остаток, ему место в `logging`.
      PRG и `ContactForm` уже сделаны (`0e10b8f`), остался только он.
      → `refactor: log contact messages instead of print`

- [ ] **`<slug:slug>/` в `urls.py` — мина.** Матчит любой односегментный путь.
      Работает только потому, что стоит последним. Заведёшь категорию со слагом
      `contacts` или `products` — она станет недостижимой молча.
      Чинить: префикс `categories/<slug:slug>/` либо запрет таких слагов в валидации.
      → `fix: avoid slug catch-all shadowing static urls`

- [ ] **`category_detail` без пагинации.** `views.py` — `PRODUCTS_PER_PAGE` объявлена,
      `templates/includes/pagination.html` написан, а в категории выводится всё разом.
      Один и тот же Read собран двумя способами.
      Закрывается переводом `category_detail` на `ListView` (раздел 4) — отдельно не делать.
      → `refactor: paginate category product list`

- [ ] **Адрес товара собирается вручную в 3 шаблонах**, хотя есть `get_absolute_url()` (`9eef2a5`).
      Во вьюхах ручных `redirect` больше нет: `CreateView` / `UpdateView` редиректят через него сами.
      `product_card.html:8`, `product_confirm_delete.html:25` — `{% url 'catalog:product_detail' product.pk %}`
      → `{{ product.get_absolute_url }}`; `product_form.html:35` — то же через `form.instance`.
      Сменится адресация товара (например, `pk` → `slug`) — править одно место, а не четыре.
      → `refactor: use Product.get_absolute_url`

- [ ] **Форма обратной связи ничего не сохраняет** — печатает в консоль.
      Решить: делать модель `Feedback` (тогда это настоящий Create) или так и оставить.
      Если модель — `ContactForm` превращается в `ModelForm` с `Meta.fields`.

---

## 3. Осознанно отложено

- [ ] **CRUD для Category на сайте.** Сейчас только админка, и этого может быть
      достаточно — категории заводит владелец магазина, не посетитель.
      Решить сознательно, а не забыть.
      Помнить: `on_delete=models.PROTECT` (`models.py:20`) не даст удалить категорию
      с товарами — упадёт `ProtectedError`, его придётся ловить, иначе 500.

- [ ] **Осиротевшие картинки.** `product.delete()` не трогает файлы в `media/products/`.
      Копятся после каждого удаления. Чинится сигналом `post_delete` или чисткой по расписанию.
      На CBV — ещё вариант: `self.object.image.delete(save=False)` в
      `ProductDeleteView.form_valid()` после `super()` (почему там — `MADE.md`, запись про CBV).

---

## 4. Перевод на CBV — идёт

**По одной вьюхе на коммит**, `views.py` и `urls.py` вместе (иначе `urls.py` сошлётся
на удалённую функцию и сайт не стартанёт). Имена маршрутов (`name=`) не меняем —
тогда все `{% url %}` в шаблонах работают без правок.

CRUD товара уже переведён (`ProductDetailView`, `ProductCreateView`, `ProductUpdateView`,
`ProductDeleteView`) — что и как, в `MADE.md`. Осталось три:

| Функция | Класс | Что пишешь сам |
|---|---|---|
| `home` | `ListView` | `queryset`, `template_name`, `context_object_name = 'products'`, `paginate_by` |
| `category_detail` | `ListView` | `template_name`, `context_object_name`, `get_queryset()`, `get_context_data()` |
| `contacts` | `SuccessMessageMixin` + `FormView` | `form_class`, `success_url`, `success_message`, `get_context_data()`, `form_valid()` |

- [ ] `home` → `ListView`, уходят ручной `Paginator` и двойная передача `page_obj`.
      Сначала решить, что делать с кривым `?page=` (последний пункт граблей ниже)
- [ ] `category_detail` → `ListView` (заодно закрывает пагинацию из раздела 2:
      `paginate_by` + `{% include 'includes/pagination.html' %}`)
- [ ] `contacts` → `FormView` — `ContactForm` и `messages` уже есть, перевод механический
- [ ] → `refactor: convert <view> to <Class>` на каждый
- [ ] После последней — `CLAUDE.md`: убрать «идёт перевод» и описание оставшихся FBV
      → `docs: update CLAUDE.md after CBV migration`

**Грабли, которые уже разобраны:**

- `success_url` в атрибуте класса — только `reverse_lazy`: класс создаётся при импорте
  `views.py`, URL-ы ещё не загружены. Зависит от объекта (`pk`) → `get_success_url()`.
- `form_class` и `fields` одновременно нельзя → `ImproperlyConfigured`.
- Переопределил `form_valid()` → обязательно `return super().form_valid(form)`,
  иначе ни сохранения, ни редиректа.
- Миксины (`LoginRequiredMixin`, `SuccessMessageMixin`) — **левее** базового класса.
  Справа молча не работают. Права из раздела 1 на CBV = `LoginRequiredMixin`
  (он и есть проверка на `dispatch()`, срабатывает на GET и POST разом).
- `category_detail`: `get_object_or_404(Category, ...)` внутри `get_queryset()` обязателен —
  иначе `<slug:slug>/` на любой мусорный путь отдаст пустую «категорию» с кодом 200.
  `template_name` задавать явно: дефолт был бы `catalog/product_list.html`.
- `ListView` на кривой `?page=999` / `?page=abc` отдаёт **404**, а сейчас
  `paginator.get_page()` молча подставляет ближайшую страницу — у `home` поведение изменится.
  Либо принять 404 (дефолт Django), либо переопределить `paginate_queryset()`
  и взять страницу через `paginator.get_page()`, как сейчас.

---

## Правила, по которым режем коммиты

1. **Каждый коммит оставляет проект запускаемым.** URL и вьюха всегда едут вместе.
2. **Один коммит = одна законченная возможность.** Граница — буква CRUD.
3. **Один коммит = одна причина изменения.** Фичи отдельно, фиксы отдельно.
4. **В коммите есть новый файл → только явный `git add`.** `git commit -am` его пропустит.
5. Сообщения: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`.
