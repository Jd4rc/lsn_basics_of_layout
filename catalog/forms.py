from django import forms
from django.core.files.uploadedfile import UploadedFile

from catalog.models import Feedback, Product

# Слова, которые нельзя использовать в названии и описании товара
FORBIDDEN_WORDS = (
    'казино',
    'криптовалюта',
    'крипта',
    'биржа',
    'дешево',
    'бесплатно',
    'обман',
    'полиция',
    'радар',
)


def find_forbidden_words(text):
    """Запрещённые слова, найденные в тексте. Регистр и «ё»/«е» не различаются."""
    normalized = text.casefold().replace('ё', 'е')
    return [word for word in FORBIDDEN_WORDS if word in normalized]


class StyleFormMixin:
    """Bootstrap-классы полям формы по типу виджета. Ставится левее ModelForm."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                css_class = 'form-check-input check-ink'
            elif isinstance(widget, forms.Select):
                css_class = 'form-select input-ink'
            else:
                css_class = 'form-control input-ink'

            # Дописываем, а не затираем: класс мог прийти из Meta.widgets
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {css_class}".strip()


# Фото товара и аватар: форматы по содержимому файла (Pillow), а не по расширению
ALLOWED_IMAGE_FORMATS = ('JPEG', 'PNG')
MAX_IMAGE_SIZE_MB = 5


def check_image(image):
    """Только JPEG и PNG не больше MAX_IMAGE_SIZE_MB. Значение для clean_<поле>."""
    # Новый файл не выбран: пусто, «очистить» или старое фото при редактировании
    if not isinstance(image, UploadedFile):
        return image

    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise forms.ValidationError(
            f'Фото весит {image.size / 1024 / 1024:.1f} МБ, а можно не больше '
            f'{MAX_IMAGE_SIZE_MB} МБ. Уменьшите или сожмите его.'
        )

    # Картинку уже открыл Pillow в forms.ImageField, формат — в image.image
    if image.image.format not in ALLOWED_IMAGE_FORMATS:
        raise forms.ValidationError(
            f'Фото в формате {image.image.format}, а принимаются только JPEG и PNG.'
        )

    return image


class ProductForm(StyleFormMixin, forms.ModelForm):
    """Форма добавления товара."""

    class Meta:
        model = Product
        fields = (
            'category',
            'name',
            'description',
            'price',
            'stock',
            'condition',
            'image',
            'is_active',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png'}),
        }
        error_messages = {
            'image': {
                'invalid_image': 'Это не картинка или файл повреждён. Загрузите JPEG или PNG.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = True

    def clean_image(self):
        return check_image(self.cleaned_data.get('image'))

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if len(name) < 3:
            raise forms.ValidationError('Название должно быть не короче трёх символов.')

        self.check_forbidden_words(name, 'Название')
        return name

    def clean_description(self):
        description = self.cleaned_data['description'].strip()

        if len(description) < 20:
            raise forms.ValidationError(
                'Описание должно быть не короче двадцати символов.'
            )

        self.check_forbidden_words(description, 'Описание')
        return description

    def clean_price(self):
        price = self.cleaned_data['price']

        if price < 0:
            raise forms.ValidationError(
                f'Цена не может быть отрицательной, а введено {price} ₽. '
                'Укажите цену больше нуля, например 1490.'
            )
        if price == 0:
            raise forms.ValidationError(
                'Цена не может быть нулевой: товар не продаётся бесплатно. '
                'Укажите цену больше нуля, например 1490.'
            )

        return price

    @staticmethod
    def check_forbidden_words(text, field_label):
        found = find_forbidden_words(text)

        if found:
            words = ', '.join(f'«{word}»' for word in found)
            raise forms.ValidationError(
                f'{field_label} содержит запрещённые слова: {words}. '
                'Уберите их и сохраните снова.'
            )


class FeedbackForm(StyleFormMixin, forms.ModelForm):
    """Форма обратной связи на странице контактов."""

    class Meta:
        model = Feedback
        fields = ('name', 'phone', 'email', 'message')
        widgets = {
            'phone': forms.TextInput(attrs={'type': 'tel'}),
            'message': forms.Textarea(attrs={'rows': 4}),
        }
        # Свои тексты вместо стандартных «Обязательное поле.»
        error_messages = {
            'name': {
                'required': 'Укажите имя.',
                'max_length': 'Имя должно быть не длиннее %(limit_value)d символов.',
            },
            'phone': {
                'required': 'Укажите телефон.',
                'max_length': 'Телефон должен быть не длиннее %(limit_value)d символов.',
            },
            'email': {
                'required': 'Укажите email.',
                'invalid': 'Введите корректный email.',
            },
            'message': {'required': 'Напишите сообщение.'},
        }
