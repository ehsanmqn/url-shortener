from datetime import datetime, timedelta
from celery import shared_task

from django.db.models import Count, Q
from django.utils import timezone

from UrlShortener_urls.models import Url, Analytics

@shared_task
def create_url_visit_task(visitor_ip, visitor_name, hash, is_pc, is_mobile, browser):
    if (is_pc):
        visitor_device = 'pc'
    elif (is_mobile):
        visitor_device = 'mobile'
    else:
        visitor_device = 'other'

    url = Url.objects.get(hash=hash)

    url.visit(visitor_ip=visitor_ip,
              visitor_device=visitor_device,
              visitor_browser=browser,
              visitor_name=visitor_name)

    return

@shared_task
def prepare_last_day_analytics():
    yesterday = timezone.make_aware(datetime.today() - timedelta(days=1), timezone.get_current_timezone())

    start_from = timezone.make_aware(datetime(yesterday.year,
                                              yesterday.month,
                                              yesterday.day),
                                     timezone.get_current_timezone())
    end_to = timezone.make_aware(datetime(yesterday.year,
                                          yesterday.month,
                                          yesterday.day, 23, 59, 59),
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
    unique_desktop_visitor = Count('visits__visitor_ip', distinct=True, filter=Q(visits__visitor_device='pc') & dateQ)
    unique_mobile_visitor = Count('visits__visitor_ip', distinct=True, filter=Q(visits__visitor_device='mobile') & dateQ)
    unique_other_devices_visitor = Count('visits__visitor_ip', distinct=True,
                                         filter=Q(visits__visitor_device='other') & dateQ)
    unique_chrome_visitor = Count('visits__visitor_ip', distinct=True, filter=Q(visits__visitor_browser='Chrome') & dateQ)
    unique_firefox_visitor = Count('visits__visitor_ip', distinct=True, filter=Q(visits__visitor_browser='Firefox') & dateQ)
    unique_other_explorers_visitor = Count('visits__visitor_ip', distinct=True,
                                           filter=Q(visits__visitor_browser='other') & dateQ)

    queryset = Url.objects \
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
        .values('uuid',
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
                'unique_other_explorers_visitor')

    Analytics.objects.bulk_create([Analytics(**q) for q in queryset])