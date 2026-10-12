from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),  # только POST, адрес — LOGOUT_REDIRECT_URL
    path('profile/', views.UserUpdateView.as_view(), name='profile'),
]
