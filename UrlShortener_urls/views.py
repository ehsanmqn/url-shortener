from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.apps import apps
from django.conf import settings


from UrlShortener_urls.models import Url
from UrlShortener_urls.permisions import IsGetOrIsAuthenticated, IsNotSuspended
from UrlShortener_urls.serializers import GetUrlsSerializer, CreateUrlsSerializer, \
    AuthenticatedUserUrlSerializer, GetUrlVisitsSerializer, UrlVisitsSerializer, GetUrlAnalyticsSerializer
from UrlShortener_urls.tasks import create_url_visit_task

class UrlView(APIView):
    # permission_classes = (IsGetOrIsAuthenticated, IsNotSuspended)
    permission_classes = (IsGetOrIsAuthenticated)
    serializer_class = CreateUrlsSerializer

    #
    # Create short URL
    #
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


    #
    # Get created urls
    #
    def get(self, request):
        if request.user.is_authenticated:
            return self.get_urls_for_authenticated_user(request)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def get_urls_for_authenticated_user(self, request):
        query_params = request.query_params.dict()

        serializer = GetUrlsSerializer(data=query_params)
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
    permission_classes = (IsAuthenticated, IsNotSuspended)

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
    permission_classes = (IsAuthenticated, IsNotSuspended)

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
    permission_classes = (IsAuthenticated, IsNotSuspended)

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


def RedirectToLongURL(request, short_url):
    url = Url.get_url_object_for_url_with_shorten_id(short_url)

    create_url_visit_task.delay(visitor_ip=request.META['REMOTE_ADDR'],
                                visitor_name=request.META['USERNAME'],
                                is_pc=request.user_agent.is_pc,
                                is_mobile=(request.user_agent.is_mobile | request.user_agent.is_tablet | request.user_agent.is_touch_capable),
                                browser=request.user_agent.browser.family,
                                url_id=url.pk)

    response = HttpResponse("", status=status.HTTP_302_FOUND)
    response['Location'] = url.url
    return response