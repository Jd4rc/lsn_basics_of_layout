import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from catalog.forms import StyleFormMixin, check_image
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Регистрация: email, пароль и его повтор (password1 и password2 даёт UserCreationForm)."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        # unique=True в модели регистр различает, а вход — нет (UserManager.get_by_natural_key)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email


class UserLoginForm(StyleFormMixin, AuthenticationForm):
    """Вход по email и паролю. Поле email у AuthenticationForm всё равно зовётся username."""

    username = forms.EmailField(
        label='Email', widget=forms.EmailInput(attrs={'autofocus': True, 'autocomplete': 'email'})
    )
    error_messages = {
        'invalid_login': 'Неверный email или пароль.',
        'inactive': 'Этот аккаунт отключён.',
    }


class UserProfileForm(StyleFormMixin, forms.ModelForm):
    """Редактирование профиля. Email и пароль здесь не меняются."""

    # Своё поле: в модели max_length=16, а с пробелами и скобками номер длиннее.
    # Длину и формат после очистки проверит phone_validator модели
    phone_number = forms.CharField(
        label='Номер телефона',
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={'type': 'tel', 'placeholder': '+375 29 123-45-67'}),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'country', 'avatar')
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png'}),
        }
        error_messages = {
            'avatar': {
                'invalid_image': 'Это не картинка или файл повреждён. Загрузите JPEG или PNG.',
            },
        }

    def clean_phone_number(self):
        # Пробелы, скобки и дефисы убираем: +375 (29) 123-45-67 → +375291234567
        return re.sub(r'[\s()-]', '', self.cleaned_data['phone_number'])

    def clean_avatar(self):
        return check_image(self.cleaned_data.get('avatar'))
