import logging

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_welcome_email(user, login_url):
    """Приветствие после регистрации."""
    try:
        send_mail(
            'Добро пожаловать в Lunch Time Aquatics',
            f'Спасибо за регистрацию! Ваш логин — {user.email}.\n\n'
            f'Войти на сайт: {login_url}',
            None,  # отправитель — DEFAULT_FROM_EMAIL
            [user.email],
        )
    except OSError:
        # Недоставленное письмо не должно ронять регистрацию. SMTPException — тоже OSError
        logger.exception('Не отправилось приветственное письмо пользователю pk=%s', user.pk)
