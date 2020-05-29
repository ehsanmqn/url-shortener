from rest_framework import serializers
from django.conf import settings
from django.contrib.auth.password_validation import validate_password

from UrlShortener.settings import USERNAME_MAX_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, PROFILE_NAME_MAX_LENGTH
from UrlShortener_auth.validators import username_characters_validator, email_not_taken_validator
from UrlShortener_auth.validators import name_characters_validator


class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH,
                                     validators=[validate_password])
    name = serializers.CharField(max_length=PROFILE_NAME_MAX_LENGTH,
                                 allow_blank=False, validators=[name_characters_validator])
    email = serializers.EmailField(validators=[email_not_taken_validator])
    phone = serializers.CharField(max_length=11, allow_blank=False)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH,
                                     allow_blank=False,
                                     validators=[username_characters_validator])
    password = serializers.CharField(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)