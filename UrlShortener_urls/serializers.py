from rest_framework import serializers
from django.conf import settings

from UrlShortener_urls.models import Url, UrlVisits
from UrlShortener_urls.validators import url_uuid_exists


class GetUrlsSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        required=False,
        max_value=20
    )

class GetUrlVisitsSerializer(serializers.Serializer):
    url_uuid = serializers.UUIDField(
        validators=[url_uuid_exists],
        required=True,
    )
    count = serializers.IntegerField(
        required=False,
        max_value=100
    )

class GetUrlAnalyticsSerializer(serializers.Serializer):
    url_uuid = serializers.UUIDField(
        validators=[url_uuid_exists],
        required=True,
    )
    count = serializers.IntegerField(
        required=False,
        max_value=20
    )

class UrlVisitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlVisits
        fields = (
            'created',
            'visitor_ip',
            'visitor_device',
            'visitor_browser'
        )

class CreateUrlsSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=settings.URL_MAX_LENGTH, required=True, allow_blank=False)
    shorten_url = serializers.CharField(max_length=settings.SHORTEN_MAX_LENTH, required=False, allow_blank=True)

class AuthenticatedUserUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = (
            'id',
            'uuid',
            'url',
            'shorten_url',
            'created',
            'creator'
        )
