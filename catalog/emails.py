import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_views_milestone_email(product, product_url):
    """Поздравление владельцу магазина: товар набрал круглое число просмотров."""
    try:
        send_mail(
            f'«{product.name}»: {product.views_count} просмотров',
            f'Поздравляю! Товар «{product.name}» набрал {product.views_count} просмотров.\n\n'
            f'Страница товара: {product_url}',
            None,  # отправитель — DEFAULT_FROM_EMAIL
            [settings.OWNER_EMAIL],
        )
    except OSError:
        # Недоставленное письмо не должно ронять страницу товара. SMTPException — тоже OSError
        logger.exception('Не отправилось письмо о %s просмотрах товара pk=%s', product.views_count, product.pk)
