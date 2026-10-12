# TODO

Только то, что **осталось**. Сделанное — в `MADE.md`.

Легенда: ✅ готово · 🔒 только через админку

---

## Где мы сейчас

**CRUD для `Product` закрыт полностью, все вьюхи — на классах (CBV).** Все три модели есть в `catalog/admin.py`,
так что у персонала CRUD полный и по остальным. С hw_27 есть пользователи (`users`): регистрация,
вход по email, профиль; страницы товара — только после входа.

| Модель | Create | Read | Update | Delete |
|---|---|---|---|---|
| **Product** | ✅ | ✅ | ✅ | ✅ |
| **Category** | 🔒 | ✅ | 🔒 | 🔒 |
| **ContactInfo** | 🔒 | ✅ | 🔒 | 🔒 |
| **Feedback** | ✅ | 🔒 | 🔒 | 🔒 |

---

## 1. Права доступа: владелец товара

Вход есть (hw_27), страницы товара закрыты `LoginRequiredMixin`. Но **любой вошедший**
редактирует и удаляет **любой** товар: `LoginRequiredMixin` проверяет только факт входа.

- [ ] `Product.owner` — `ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)`,
      `null=True` нужен для уже существующих товаров
- [ ] Владелец проставляется в `ProductCreateView.form_valid()` (`form.instance.owner = self.request.user`),
      в `ProductForm.Meta.fields` поля `owner` нет
- [ ] `ProductUpdateView` / `ProductDeleteView`: `get_queryset()` с `filter(owner=self.request.user)` —
      чужой товар даёт 404. Кнопки «Редактировать» / «Удалить» в `product_detail.html` — только владельцу
- [ ] → `feat: restrict product editing to its owner`

---

## 2. Отдельные правки

Разные причины изменения — разные коммиты.

- [ ] **`<slug:slug>/` в `urls.py` — мина.** Матчит любой односегментный путь.
      Работает только потому, что стоит последним. Заведёшь категорию со слагом
      `contacts` или `admin` — она станет недостижимой молча (`products` не задет:
      маршрута ровно `products/` нет).
      Чинить: префикс `categories/<slug:slug>/` либо запрет таких слагов в валидации.
      → `fix: avoid slug catch-all shadowing static urls`

- [ ] **Адрес товара собирается вручную в 3 шаблонах**, хотя есть `get_absolute_url()` (`9eef2a5`).
      Во вьюхах ручных `redirect` больше нет: `CreateView` / `UpdateView` редиректят через него сами.
      `product_card.html:8`, `product_confirm_delete.html:25` — `{% url 'catalog:product_detail' product.pk %}`
      → `{{ product.get_absolute_url }}`; `product_form.html:35` — то же через `form.instance`.
      Сменится адресация товара (например, `pk` → `slug`) — править одно место, а не четыре.
      → `refactor: use Product.get_absolute_url`

- [ ] **Цикл по полям всё ещё продублирован в двух шаблонах.** `templates/includes/form_fields.html`
      уже есть (hw_27, им пользуются шаблоны `users`), но `product_form.html` и `contacts.html` выводят
      поля своим блоком. Перевести `contacts.html` на include: получит `form.non_field_errors`,
      которого там нет. В `product_form.html` чекбокс выводится через `form-check` — include
      это пока не умеет, сначала добавить ветку для `field.widget_type == 'checkbox'`.
      → `refactor: use form fields include in catalog templates`

- [ ] **Тестов нет.** Поток hw_27 (регистрация, письмо, вход, выход, редирект гостя, профиль)
      проверялся тестовым клиентом из скрипта. Переписать в `users/tests.py` — `mail.outbox`
      ловит письмо, `assertRedirects` — `?next=`. Нужно право `CREATEDB` у `DB_USER`.
      → `test: cover registration, login and product access`

---

## 3. Осознанно отложено

- [ ] **Восстановление пароля.** В hw_27 не входило, забытый пароль меняется только в админке.
      Четыре готовые вьюхи `PasswordReset*View`. Грабли: внутри у них имена маршрутов без
      namespace (`password_reset_done`, `password_reset_complete`) — под `users:` нужен свой
      `success_url = reverse_lazy('users:...')` и свой URL в шаблоне письма.

- [ ] **CRUD для Category на сайте.** Сейчас только админка, и этого может быть
      достаточно — категории заводит владелец магазина, не посетитель.
      Решить сознательно, а не забыть.
      Помнить: `on_delete=models.PROTECT` (`models.py:21`) не даст удалить категорию
      с товарами — упадёт `ProtectedError`, его придётся ловить, иначе 500.

- [ ] **Осиротевшие картинки.** `product.delete()` не трогает файлы в `media/products/`.
      Копятся после каждого удаления. То же с аватаром: при замене или «очистить» в профиле
      старый файл остаётся в `media/users/avatars/`. Чинится сигналом `post_delete` или чисткой по расписанию.
      На CBV — ещё вариант: `self.object.image.delete(save=False)` в
      `ProductDeleteView.form_valid()` после `super()` (почему там — `MADE.md`, запись про CBV).

- [ ] **Письма уходят внутри запроса.** Сотый посетитель товара и только что
      зарегистрированный пользователь (`users/emails.py`) ждут SMTP,
      при недоступном сервере — до `timeout` (10 с) из `MAILERS`. Для учебного проекта
      нормально, на бою — очередь задач (Celery) и отправка в фоне.

---

## Правила, по которым режем коммиты

1. **Каждый коммит оставляет проект запускаемым.** URL и вьюха всегда едут вместе.
2. **Один коммит = одна законченная возможность.** Граница — буква CRUD.
3. **Один коммит = одна причина изменения.** Фичи отдельно, фиксы отдельно.
4. **В коммите есть новый файл → только явный `git add`.** `git commit -am` его пропустит.
5. Сообщения: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`.
