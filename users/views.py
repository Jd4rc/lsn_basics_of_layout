from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.emails import send_welcome_email
from users.forms import UserLoginForm, UserProfileForm, UserRegisterForm
from users.models import User


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        response = super().form_valid(form)  # сохраняет пользователя в self.object
        login(self.request, self.object)
        send_welcome_email(self.object, self.request.build_absolute_uri(reverse('users:login')))
        return response


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True  # уже вошедшего — сразу на LOGIN_REDIRECT_URL


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')
    success_message = 'Профиль сохранён.'

    def get_object(self, queryset=None):
        # Только свой профиль: pk в адресе нет, чужой не открыть.
        # Свежая копия, а не request.user: невалидная форма меняет поля объекта,
        # и шапка с аватаром показали бы несохранённые данные
        return self.model.objects.get(pk=self.request.user.pk)
