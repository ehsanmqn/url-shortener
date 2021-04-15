from django.db import transaction
from django.http import HttpResponse
from django.apps import apps
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from UrlShortener_urls.models import Url
from UrlShortener_urls.serializers import GetShortUrlSerializer, CreateShortUrlSerializer, \
    AuthenticatedUserUrlSerializer, GetUrlVisitsSerializer, UrlVisitsSerializer, GetUrlAnalyticsSerializer
from UrlShortener_urls.tasks import create_url_visit_task

class UrlView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated)
    serializer_class = CreateShortUrlSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.on_valid_post_data(serializer.validated_data, request.user)

    def on_valid_post_data(self, data, user):
        url = data.get('url')

        with transaction.atomic():
            url = user.create_short_url(url=url)

        return Response({
            'url': settings.BASE_URL + settings.SHORT_URL_PREFIX + url.shorten_url,
            },
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        query_params = request.query_params.dict()

        serializer = GetShortUrlSerializer(data=query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        count = data.get('count', 10)

        user = request.user

        urls = user.get_timeline_urls(count=count)
        urls = urls.order_by('-id')

        urls_serializer_data = AuthenticatedUserUrlSerializer(urls, many=True, context={"request": request}).data

        return Response(urls_serializer_data, status=status.HTTP_200_OK)

def get_url_id_for_url_uuid(url_uuid):
    Url = apps.get_model('UrlShortener_urls.Url')
    url = Url.objects.values('id').get(uuid=url_uuid)
    return url['id']

class UrlVisitView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated)

    def get(self, request):
        query_params = request.query_params.dict()

        serializer = GetUrlVisitsSerializer(data=query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        url_uuid = data.get('url_uuid')
        count = data.get('count', 10)

        user = request.user
        url_id = get_url_id_for_url_uuid(url_uuid)

        url_visits = user.get_visits_for_url_with_id(url_id=url_id).order_by('-created')[:count]

        url_visits_serializer = UrlVisitsSerializer(url_visits, many=True, context={"request": request})

        return Response(url_visits_serializer.data, status=status.HTTP_200_OK)


class UrlVisitAnalyticsView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated)

    def post(self, request):
        request_data = request.data

        serializer = GetUrlAnalyticsSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        url_uuid = data.get('url_uuid')
        start_time=data.get('start_time')
        end_time=data.get('end_time')

        user = request.user
        url_id = get_url_id_for_url_uuid(url_uuid)

        url_visits = user.get_visit_analytics_for_url(url_id=url_id, start_time=start_time, end_time=end_time)

        return Response(url_visits, status=status.HTTP_200_OK)


class UrlVisitorsAnalyticsView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated)

    def post(self, request):
        request_data = request.data

        serializer = GetUrlAnalyticsSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        url_uuid = data.get('url_uuid')
        start_time = data.get('from')
        end_time = data.get('to')

        user = request.user
        url_id = get_url_id_for_url_uuid(url_uuid)

        url_visits = user.get_visitor_analytics_for_url(url_id=url_id, start_time=start_time, end_time=end_time)

        return Response(url_visits, status=status.HTTP_200_OK)


def RedirectToLongURL(request, shorten_url):
    create_url_visit_task.delay(visitor_ip=request.META['REMOTE_ADDR'],
                                visitor_name=request.META['USERNAME'],
                                is_pc=request.user_agent.is_pc,
                                is_mobile=(request.user_agent.is_mobile | request.user_agent.is_tablet | request.user_agent.is_touch_capable),
                                browser=request.user_agent.browser.family,
                                shorten_url=shorten_url)

    response = HttpResponse("", status=status.HTTP_302_FOUND)
    response['Location'] = Url.get_source_url_with_shorten_url(shorten_url=shorten_url)
    return response