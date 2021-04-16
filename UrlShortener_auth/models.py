from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.utils import six
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token

from UrlShortener.settings import USERNAME_MAX_LENGTH

class User(AbstractUser):
    name = models.CharField(blank=False, null=False, max_length=100)
    email = models.EmailField('email address', unique=True, null=False, blank=False)
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        blank=False,
        null=False,
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text='Required. %(username_max_length)d characters or fewer. Letters, digits and _ only.' % {
            'username_max_length': USERNAME_MAX_LENGTH},
        validators=[username_validator],
        error_messages={
            'unique': "A user with this username already exists.",
        },
    )

    phone = models.CharField(
        default='',
        blank=True,
        null=False,
        max_length=11,
        unique=True,
    )

    JWT_TOKEN_TYPE_CHANGE_EMAIL = 'CE'
    JWT_TOKEN_TYPE_PASSWORD_RESET = 'PR'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    @classmethod
    def create_user(cls, username, email=None, password=None, name=None, phone=None):
        return cls.objects.create_user(username, email=email, password=password, name=name, phone=phone)

    @classmethod
    def is_email_taken(cls, email):
        try:
            cls.objects.get(email=email)
            return True
        except User.DoesNotExist:
            return False

    @classmethod
    def is_phone_taken(cls, phone):
        try:
            cls.objects.get(phone=phone)
            return True
        except User.DoesNotExist:
            return Falsee

    def _reset_auth_token(self):
        self.auth_token.delete()
        bootstrap_user_auth_token(user=self)


@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid='bootstrap_auth_token')
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """"
    Create a token for all users
    """
    if created:
        bootstrap_user_auth_token(instance)

def bootstrap_user_auth_token(user):
    return Token.objects.create(user=user)
