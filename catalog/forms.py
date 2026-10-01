from django import forms

from catalog.models import Feedback, Product


class StyleFormMixin:
    """Bootstrap-классы полям формы по типу виджета. Ставится левее ModelForm."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(widget, forms.Select):
                css_class = 'form-select input-ink'
            else:
                css_class = 'form-control input-ink'

            # Дописываем, а не затираем: класс мог прийти из Meta.widgets
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {css_class}".strip()


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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = True

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if len(name) < 3:
            raise forms.ValidationError('Название должно быть не короче трёх символов.')

        return name

    def clean_description(self):
        description = self.cleaned_data['description'].strip()

        if len(description) < 20:
            raise forms.ValidationError(
                'Описание должно быть не короче двадцати символов.'
            )

        return description

    def clean_price(self):
        price = self.cleaned_data['price']

        if price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля.')

        return price


class FeedbackForm(StyleFormMixin, forms.ModelForm):
    """Форма обратной связи на странице контактов."""

    class Meta:
        model = Feedback
        fields = ('name', 'phone', 'email', 'message')
        widgets = {
            'phone': forms.TextInput(attrs={'type': 'tel'}),
            'message': forms.Textarea(attrs={'rows': 4}),
        }
        # LANGUAGE_CODE = 'en-us': стандартные тексты ошибок были бы английскими
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
