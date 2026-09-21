from django import forms

from catalog.models import Product


class ProductForm(forms.ModelForm):
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
            'category': forms.Select(attrs={'class': 'form-select input-ink'}),
            'name': forms.TextInput(attrs={'class': 'form-control input-ink'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control input-ink', 'rows': 4}
            ),
            'price': forms.NumberInput(
                attrs={'class': 'form-control input-ink', 'step': '0.01'}
            ),
            'stock': forms.NumberInput(attrs={'class': 'form-control input-ink'}),
            'condition': forms.Select(attrs={'class': 'form-select input-ink'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control input-ink'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
