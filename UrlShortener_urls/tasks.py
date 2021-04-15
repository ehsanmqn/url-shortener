from datetime import datetime, timedelta
from celery import shared_task

from django.db.models import Sum, Count, Q
from django.utils import timezone

from UrlShortener_urls.models import Url, Visit, Analytics

@shared_task
def create_url_visit_task(visitor_ip, visitor_name, shorten_url, is_pc, is_mobile, browser):
    if (is_pc):
        visitor_device = 'pc'
    elif (is_mobile):
        visitor_device = 'mobile'
    else:
        visitor_device = 'other'

    url = Url.objects.get(shorten_url=shorten_url)

    url.visit(visitor_ip=visitor_ip,
              visitor_device=visitor_device,
              visitor_browser=browser,
              visitor_name=visitor_name)

    return

@shared_task
def prepare_last_day_analytics():
    start_date = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
    end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')

    yesterday = timezone.make_aware(datetime.today() - timedelta(days=1), timezone.get_current_timezone())
    total_visit = Count('visits', filter=Q(visits__created_at__gt=yesterday))
    desktop_visit = Count('visits', filter=Q(visits__visitor_device='pc')&Q(visits__created_at__gt=yesterday))
    mobile_visit = Count('visits', filter=Q(visits__visitor_device='mobile')&Q(visits__created_at__gt=yesterday))
    other_devices_visit = Count('visits', filter=Q(visits__visitor_device='other')&Q(visits__created_at__gt=yesterday))
    chrome_visit = Count('visits', filter=Q(visits__visitor_browser='Chrome')&Q(visits__created_at__gt=yesterday))
    firefox_visit = Count('visits', filter=Q(visits__visitor_browser='Firefox')&Q(visits__created_at__gt=yesterday))
    other_explorers_visit = Count('visits', filter=Q(visits__visitor_browser='other')&Q(visits__created_at__gt=yesterday))


    queryset = Url.objects\
        .annotate(total_visit=total_visit)\
        .annotate(desktop_visit=desktop_visit)\
        .annotate(mobile_visit=mobile_visit)\
        .annotate(other_devices_visit=other_devices_visit)\
        .annotate(chrome_visit=chrome_visit)\
        .annotate(firefox_visit=firefox_visit)\
        .annotate(other_explorers_visit=other_explorers_visit)\
        .values('uuid', 'total_visit', 'desktop_visit', 'mobile_visit', 'other_devices_visit', 'chrome_visit', 'chrome_visit', 'firefox_visit', 'other_explorers_visit')

    Analytics.objects.bulk_create([Analytics(q) for q in queryset])