from datetime import timedelta, date, datetime

from django.db import transaction
from django.http import HttpResponse
from django.conf import settings
from django.apps import apps
from django.db.models import Sum, Count, Q
from django.utils import timezone

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from UrlShortener_urls.models import Url
from UrlShortener_urls.serializers import AnalyticsModelSerializer, CreateShortUrlSerializer, UrlModelSerializer
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
            'url': settings.BASE_URL + settings.SHORT_URL_PREFIX + url.hash,
            },
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        user = request.user

        UrlModel = apps.get_model('UrlShortener_urls.Url')
        queryset = UrlModel.objects.filter(creator=user)

        serialized_data = UrlModelSerializer(queryset,
                                                  many=True,
                                                  context={"request": request}).data

        return Response(serialized_data, status=status.HTTP_200_OK)


class RetrieveUrlLastDaysVisitAnalytics(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (FormParser, MultiPartParser,)
    serializer_class = AnalyticsModelSerializer

    AnalyticModel = apps.get_model('UrlShortener_urls.Analytics')
    queryset = AnalyticModel.objects.all()

    def get_queryset(self):
        UrlModel = apps.get_model('UrlShortener_urls.Url')
        url = UrlModel.objects.get(pk=self.kwargs.get('pk'))

        days = int(self.kwargs.get('days'))

        if days > 0:
            start_from = date.today() - timedelta(days=days)
            end_to = date.today() - timedelta(days=1)

            return self.queryset.filter(uuid=url.uuid, created_at__range=[start_from, end_to]) \
                .aggregate(
                    total_visit=Sum('total_visit'),
                    desktop_visit=Sum('desktop_visit'),
                    mobile_visit=Sum('mobile_visit'),
                    other_devices_visit=Sum('other_devices_visit'),
                    chrome_visit=Sum('chrome_visit'),
                    firefox_visit=Sum('firefox_visit'),
                    other_explorers_visit=Sum('other_explorers_visit'),
                    unique_visitor=Sum('unique_visitor'),
                    unique_mobile_visitor=Sum('unique_mobile_visitor'),
                    unique_other_devices_visitor=Sum('unique_other_devices_visitor'),
                    unique_chrome_visitor=Sum('unique_chrome_visitor'),
                    unique_firefox_visitor=Sum('unique_firefox_visitor'),
                    unique_other_explorers_visitor=Sum('unique_other_explorers_visitor')
                )
        else:
            end_to = timezone.make_aware(datetime.today(), timezone.get_current_timezone())
            start_from = timezone.make_aware(datetime(end_to.year,
                                                      end_to.month,
                                                      end_to.day),
                                             timezone.get_current_timezone())

            dateQ = Q(visits__created_at__range=[start_from, end_to])

            total_visit = Count('visits', filter=dateQ)
            desktop_visit = Count('visits', filter=Q(visits__visitor_device='pc') & dateQ)
            mobile_visit = Count('visits', filter=Q(visits__visitor_device='mobile') & dateQ)
            other_devices_visit = Count('visits', filter=Q(visits__visitor_device='other') & dateQ)
            chrome_visit = Count('visits', filter=Q(visits__visitor_browser='Chrome') & dateQ)
            firefox_visit = Count('visits', filter=Q(visits__visitor_browser='Firefox') & dateQ)
            other_explorers_visit = Count('visits', filter=Q(visits__visitor_browser='other') & dateQ)

            unique_visitor = Count('visits__visitor_ip', distinct=True, filter=dateQ)
            unique_desktop_visitor = Count('visits__visitor_ip', distinct=True,
                                           filter=Q(visits__visitor_device='pc') & dateQ)
            unique_mobile_visitor = Count('visits__visitor_ip', distinct=True,
                                          filter=Q(visits__visitor_device='mobile') & dateQ)
            unique_other_devices_visitor = Count('visits__visitor_ip', distinct=True,
                                                 filter=Q(visits__visitor_device='other') & dateQ)
            unique_chrome_visitor = Count('visits__visitor_ip', distinct=True,
                                          filter=Q(visits__visitor_browser='Chrome') & dateQ)
            unique_firefox_visitor = Count('visits__visitor_ip', distinct=True,
                                           filter=Q(visits__visitor_browser='Firefox') & dateQ)
            unique_other_explorers_visitor = Count('visits__visitor_ip', distinct=True,
                                                   filter=Q(visits__visitor_browser='other') & dateQ)

            queryset = Url.objects.filter(pk=self.kwargs.get('pk')) \
                .annotate(total_visit=total_visit) \
                .annotate(desktop_visit=desktop_visit) \
                .annotate(mobile_visit=mobile_visit) \
                .annotate(other_devices_visit=other_devices_visit) \
                .annotate(chrome_visit=chrome_visit) \
                .annotate(firefox_visit=firefox_visit) \
                .annotate(other_explorers_visit=other_explorers_visit) \
                .annotate(unique_visitor=unique_visitor) \
                .annotate(unique_desktop_visitor=unique_desktop_visitor) \
                .annotate(unique_mobile_visitor=unique_mobile_visitor) \
                .annotate(unique_other_devices_visitor=unique_other_devices_visitor) \
                .annotate(unique_chrome_visitor=unique_chrome_visitor) \
                .annotate(unique_firefox_visitor=unique_firefox_visitor) \
                .annotate(unique_other_explorers_visitor=unique_other_explorers_visitor) \
                .values('total_visit',
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
                        'unique_other_explorers_visitor')

            return queryset[0]

    def get(self, request, *args, **kwargs):
        return Response({
            "analytics": self.get_queryset()
        }, status=status.HTTP_200_OK)


def RedirectToLongURL(request, hash):

    create_url_visit_task.delay(visitor_ip=request.META['REMOTE_ADDR'],
                                visitor_name=request.META['USERNAME'],
                                is_pc=request.user_agent.is_pc,
                                is_mobile=(request.user_agent.is_mobile | request.user_agent.is_tablet | request.user_agent.is_touch_capable),
                                browser=request.user_agent.browser.family,
                                hash=hash)

    response = HttpResponse("", status=status.HTTP_302_FOUND)
    response['Location'] = Url.get_source_url_with_hash(hash=hash)
    return response