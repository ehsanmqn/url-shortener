import re
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError, NotFound

from UrlShortener_auth.models import User


def username_characters_validator(username):
    if not re.match('^[a-zA-Z0-9_.@]*$', username):
        raise ValidationError(
            _('Usernames can only contain alphanumeric characters, periods and underscores.'),
        )

def username_not_taken_validator(username):
    if User.is_username_taken(username):
        raise ValidationError(
            _('The username is already taken.'),
        )

def email_not_taken_validator(email):
    if User.is_email_taken(email):
        raise ValidationError(
            _('An account for the email already exists.'),
        )

def name_characters_validator(name):
    if '>' in name or '<' in name:
        raise ValidationError(
            _('Names can\'t contain < or >.'),
        )