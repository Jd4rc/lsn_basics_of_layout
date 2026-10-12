# Сделано

Короткий журнал. Что осталось — в `TODO.md`. Подробности изменений — в `git log`.

## CRUD для Product — закрыт

| Операция | Статус | Коммит | На CBV |
|---|---|---|---|
| Create | ✅ | было до этой работы | `3cf2afb` |
| Read (список + карточка) | ✅ | было до этой работы | карточка `382ad60`, главная `refactor: convert home to ListView`, категория `refactor: convert category_detail to ListView` |
| Update | ✅ | `7b0bcab` | `5421d3b` |
| Delete | ✅ | `f0e18e9` | `e10ae2a` |

---

## 2026-10-10 · hw_27: пользователи и вход · `refactor: extract image check for reuse` `feat: switch built-in messages to Russian` `feat: add users app with email-based custom user model` `feat: add registration, login, logout and profile` `feat: require login for product pages` `docs: update README`

- Приложение `users`: `User(AbstractUser)` без `username`, `USERNAME_FIELD = 'email'`, поля `avatar`,
  `phone_number`, `country`; `UserManager` (вход по email без учёта регистра), `UserAdmin` под email.
- Регистрация (`UserCreationForm`, сразу вход и письмо), вход (`LoginView`), выход POST-кнопкой, профиль.
  `LoginRequiredMixin` на карточке, создании, правке и удалении товара; `LANGUAGE_CODE = 'ru'`.

**Знать:** `AUTH_USER_MODEL` на смигрированной базе — только после `migrate auth zero` (удалил
пользователей и `django_admin_log`), иначе `InconsistentMigrationHistory`. `UserCreationForm.clean_username`
жёстко про `username`: дубль email другим регистром ловит свой `clean_email`. Длину поля формы Django
проверяет до `clean_<поле>`, поэтому у телефона в форме `max_length=30`, а 16 — в модели после очистки.

## 2026-10-05 · Критерии hw_26 · `feat: forbid spam words in product name and description` `fix: explain rejected product price` `style: render product checkbox as form-check` `feat: validate product image format and size` `chore: replace load-dotenv with python-dotenv` `chore: ignore OS junk files`

- `FORBIDDEN_WORDS` в `catalog/forms.py`, `clean_name` / `clean_description` проверяют через
  `casefold()` и `ё`→`е`. Отрицательная и нулевая цена получили разные сообщения с введённым значением.
- `clean_image`: только JPEG/PNG и не больше 5 МБ. Формат берётся из `image.image.format`: его уже
  определил Pillow внутри `forms.ImageField`, так что GIF, переименованный в `.png`, не пройдёт.
- Чекбокс: `form-check` в `product_form.html` + класс `check-ink` в `style.css`.
- `load-dotenv` был обёрткой, а код импортирует `python-dotenv`, который приезжал транзитивно.
  `.DS_Store`, `Thumbs.db`, `desktop.ini` в `.gitignore`.

**Знать:** при редактировании без нового файла в `cleaned_data['image']` лежит старый `FieldFile`
(у него нет `.image`), а при «очистить» там `False`. Поэтому проверяется только `UploadedFile`.
Проверка по подстроке: `обмана` ловится, `полиции` — нет. `poetry add` падал с «нет сети»,
а внутри `-v` был `Permission denied` на файл кэша. Помог `--no-cache`.

## 2026-10-01 · Стили форм в миксине · `refactor: extract form styling mixin`

- `StyleFormMixin` в `catalog/forms.py`: в `__init__` проходит по `self.fields` и дописывает
  `class` по типу виджета (`form-check-input` / `form-select input-ink` / `form-control input-ink`).
  `ProductForm` и `FeedbackForm` наследуют его левее `ModelForm`; в `Meta.widgets` остались только
  `rows`, `step` и `type="tel"`.

**Знать:** класс дописывается к уже стоящему, а не затирает его (`attrs.update({'class': ...})`
затёр бы). Миксин левее `ModelForm`: справа его `__init__` не вызовется. Поля копируются на каждую
форму (`deepcopy(base_fields)`), поэтому классы не копятся между запросами. Проверено: HTML обеих форм
(пустые, с ошибками, с товаром) до и после совпал с точностью до порядка атрибутов.

## 2026-10-01 · Обратная связь сохраняется · `feat: add Feedback model` `feat: save contact form messages as Feedback`

- `Feedback` (`name`, `phone`, `email`, `message`, `created_at`), миграция `0006_feedback`, в админке
  с поиском. `ContactForm(forms.Form)` → `FeedbackForm(ModelForm)`, `ContactFormView(FormView)` →
  `FeedbackCreateView(SuccessMessageMixin, CreateView)`. `print` из `form_valid()` убран — вьюха без своей логики.

**Знать:** тексты ошибок теперь в `Meta.error_messages` (словарь по полям), а не в полях формы.
`template_name` задан явно: дефолтный был бы `feedback_form.html`, а страница — `contacts.html`.
`SuccessMessageMixin` с `CreateView` работает так же, как с `FormView`. Email обязательный.
Маршрут и его имя `catalog:contacts` прежние. Проверено тест-клиентом в транзакции с откатом:
пустой POST (4 ошибки), плохой email, успех → 302, сообщение показывается один раз, `max_length`.

## 2026-09-27 · Письмо на 100 просмотров · `feat: email owner when product hits 100 views`

- `catalog/emails.py` — `send_views_milestone_email()`: тема, текст со ссылкой, получатель `OWNER_EMAIL`;
  ошибка SMTP (`OSError`) пишется в лог, страница не падает.
- `ProductDetailView.get_object()` — `UPDATE` и чтение нового значения в одной `transaction.atomic()`,
  на `VIEWS_MILESTONE = 100` шлёт письмо. `settings.py` — `MAILERS`: SMTP из `.env` или console.
- `.env.example`, `README.md` (раздел «Письмо на 100 просмотров»), `CLAUDE.md`.

**Знать:** в Django 6.1 почта — `MAILERS` с `OPTIONS` (`host`, `port`, `use_ssl`, `timeout`), `EMAIL_*`
устарели. Читать счётчик после `UPDATE` надо в той же транзакции: `UPDATE` держит строку, и
каждый запрос видит своё значение — 20 одновременных открытий с 90 дали одно письмо. Без
`timeout` недоступный SMTP подвесил бы страницу. В консоли письмо в base64 — это нормально.

## 2026-09-27 · Счётчик просмотров товара · `feat: count product views`

- `Product.views_count` (`PositiveIntegerField`, `default=0`), миграция `0005_product_views_count`,
  в админке только для чтения. `ProductDetailView.get_object()` прибавляет 1, на странице товара —
  «Просмотры: N». Правка, удаление и списки просмотры не считают. Строка в `CLAUDE.md`, README — отдельно.

**Знать:** прибавляем через `filter(pk=...).update(views_count=F('views_count') + 1)`, а не `save()`:
`save()` пишет все поля, `auto_now` сдвигал бы «Обновлён» на каждый просмотр, а два одновременных
открытия затирали бы друг друга. `F()` считает в самой базе. Фикстура без поля грузится — берётся `default=0`.

## 2026-09-27 · README под сдачу · `docs: update README`

- Таблица страниц с колонкой «Вьюха» и маршрутами правки и удаления, новые разделы «Вьюхи»,
  «Удаление товара», «Известные ограничения»; описание контактов и формы товара — под CBV.
- Убрано устаревшее: `catalog.views.contacts`, «валидация и редирект пока не реализованы».

## 2026-09-27 · Контакты на `FormView` · `refactor: convert contacts to FormView`

- `contacts` → `ContactFormView(SuccessMessageMixin, FormView)`: `get_context_data()` добавляет
  `contact_info`, `form_valid()` печатает сообщение и зовёт `super()`. Функций во `views.py` не осталось.
- `CLAUDE.md` — «идёт перевод» → «все вьюхи на CBV», грабли CBV переехали туда из `TODO.md`
  (`docs: update CLAUDE.md after CBV migration`)

**Знать:** `success_message` форматируется как `% form.cleaned_data`: `%(name)s` подставит имя,
а голый `%` в тексте надо писать `%%`, иначе 500 после отправки. OPTIONS теперь отвечает
пустым 200 с `Allow`, TRACE — 405; у функции оба рендерили страницу. GET и POST — байт в байт как были.

## 2026-09-27 · Категория на `ListView` · `refactor: convert category_detail to ListView`

- `category_detail` → `CategoryProductListView(NearestPageMixin, ListView)`: `get_queryset()`
  ищет категорию по слагу, `get_context_data()` отдаёт её в шаблон. В `category_detail.html` — пагинация.
- `paginate_queryset()` из `ProductListView` вынесен в `NearestPageMixin`, главная — на нём же.

**Знать:** `get_object_or_404` — внутри `get_queryset()`, иначе `<slug:slug>/` на мусорный путь
отдаст пустую «категорию» с кодом 200. Категорию там же кладём на `self`: `get_queryset()`
вызывается раньше `get_context_data()`. Миксин — левее `ListView`, справа молча не сработает.

## 2026-09-25 · Главная на `ListView` · `refactor: convert home to ListView`

- `home` → `ProductListView(ListView)`: `queryset`, `template_name = 'catalog/home.html'`,
  `context_object_name`, `paginate_by`. Ручной `Paginator` и двойной `page_obj` ушли.

**Знать:** `ListView` на кривой `?page=` (`abc`, `999`, `0`) отдаёт 404 — ближайшую страницу,
как раньше, сохраняет переопределённый `paginate_queryset()` через `get_page()`.
`products` в шаблоне теперь `page.object_list`, а не `Page` — для `{% for %}` без разницы.

## 2026-09-25 · CRUD товара на CBV · `382ad60` `3cf2afb` `5421d3b` `e10ae2a`

| Было | Стало | Что написано руками |
|---|---|---|
| `product_detail` | `ProductDetailView(DetailView)` | `model` |
| `product_create` | `ProductCreateView(CreateView)` | `model`, `form_class` |
| `product_update` | `ProductUpdateView(UpdateView)` | `model`, `form_class` |
| `product_delete` | `ProductDeleteView(DeleteView)` | `model`, `success_url = reverse_lazy('catalog:home')` |

- `views.py` — четыре функции → четыре класса по 2–3 строки
- `urls.py` — `views.<Класс>.as_view()`, имена маршрутов прежние, шаблоны не тронуты
- `CLAUDE.md` — «FBV сознательно, CBV отложен» → «идёт перевод» (`0455d12`)

**Знать:**
- Шаблоны и переменные — по дефолтам: `<app>/<model>_detail.html`, `_form.html`
  (общий у Create и Update), `_confirm_delete.html`; в контексте `product` (имя модели) и `object`.
- `model` у `CreateView` нужна, хотя модель есть в `ProductForm.Meta`: из неё собирается
  имя шаблона, а объекта на GET ещё нет.
- `CreateView` / `UpdateView` без `success_url` редиректят на `get_absolute_url()` объекта.
  `request.FILES` форма получает сама — `get_form_kwargs()` на POST.
- `UpdateView` = `CreateView` + `self.object = self.get_object()` (404 на чужой `pk`)
  + `instance=self.object` в форму. Ровно то, что в функции было руками в обеих ветках.
- `DeleteView` в `get_absolute_url()` не ходит (страницы удалённого товара нет) — без
  `success_url` падает `ImproperlyConfigured`, причём **после** удаления. В атрибуте класса
  только `reverse_lazy`: атрибут вычисляется при импорте `views.py`, а импортирует его
  недочитанный `urls.py`.
- С Django 4.0 `DeleteView` удаляет через пустую форму: POST → `form_valid()` →
  `self.object.delete()`. Своя логика удаления — в `form_valid()`, `delete()` на POST
  не вызывается. HTTP-метод DELETE у неё тоже обрабатывается, но без CSRF-токена — 403.

**Как проверяли:** перед каждым переводом снимали ответы старой вьюхи тест-клиентом —
GET, 404, POST с ошибками, успешный POST, картинка (загрузка, замена, очистка), запросы
без CSRF — в транзакции с откатом. После перевода то же самое и `diff`: совпало байт в байт
(CSRF-токен и `pk` вычищены). Тестовые файлы из `media/products/` удалялись.

## 2026-09-25 · Заметки и CLAUDE.md в репозитории · `569a268` `d30ac76` `5ba43f6`

- `.gitignore` — убраны `/TODO.md`, `/MADE.md`, `/CLAUDE.md`: запись от 23.09 ниже больше не действует
- `CLAUDE.md` — «локальные заметки (в `.gitignore`)» → «заметки пользователя»;
  правило: коммитит пользователь сам, Claude только предлагает разбивку и сообщения

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
Отменено 2026-09-25 (`569a268`) — заметки теперь в репозитории.

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

Перевод всех вьюх на классы снаружи не виден (кроме пагинации в категории — ниже),
и так и задумано: адреса, страницы и поведение те же. Выигрыш внутри: вьюхи CRUD стали
объявлениями на 2–3 строки, вся механика (404, `instance`, `request.FILES`, редиректы,
пагинация, сообщения после отправки) — в Django, а не в нашем коде.

Категория теперь листается по 6 товаров, как главная, а кривой `?page=` не даёт 404.
Раньше выводилось всё разом — пока в категориях до 4 товаров, разницы не видно.
