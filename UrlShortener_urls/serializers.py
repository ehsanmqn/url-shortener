from rest_framework import serializers
from django.conf import settings

from UrlShortener_urls.models import Url, Visit, Analytics
from UrlShortener_urls.validators import url_uuid_exists


class GetShortUrlSerializer(serializers.Serializer):
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

class CreateShortUrlSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=settings.URL_MAX_LENGTH, required=True, allow_blank=False)
    shorten_url = serializers.CharField(max_length=settings.SHORTEN_MAX_LENTH, required=False, allow_blank=True)


class UrlModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = (
            'id',
            'uuid',
            'url',
            'shorten_url',
            'created_at'
        )


class AnalyticsModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'uuid',
            'total_visit',
            'desktop_visit',
            'mobile_visit',
            'other_devices_visit',
            'chrome_visit',
            'firefox_visit',
            'other_explorers_visit',
            'unique_visitor',
            'unique_desktop_visitor',
            'unique_mobile_visitor',
            'unique_other_devices_visitor',
            'unique_chrome_visitor',
            'unique_firefox_visitor',
            'unique_other_explorers_visitor',
            'created_at'
        )

        model = Analytics


class VisitModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'created',
            'visitor_ip',
            'visitor_device',
            'visitor_browser'
        )

        model = Visit