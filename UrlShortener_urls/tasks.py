from datetime import datetime, timedelta
from celery import shared_task

from UrlShortener_urls.models import Url

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
def prepare_analytics():
    start_time = datetime.now() - timedelta(1)
    pass