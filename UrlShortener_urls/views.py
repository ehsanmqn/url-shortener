from django.db import transaction
from django.http import HttpResponse
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from UrlShortener_urls.models import Url
from UrlShortener_urls.serializers import GetShortUrlSerializer, CreateShortUrlSerializer, AuthenticatedUserUrlSerializer
from UrlShortener_urls.tasks import create_url_visit_task

class UrlView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)
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