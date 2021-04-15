from celery import shared_task
from UrlShortener_urls.models import Url

@shared_task
def create_url_visit_task(visitor_ip, visitor_name, shorten_url, is_pc, is_mobile, browser):
    if (is_pc):
        visitor_device = 1
    elif (is_mobile):
        visitor_device = 2
    else:
        visitor_device = 3

    url = Url.objects.get(shorten_url=shorten_url)

    url.visit(visitor_ip=visitor_ip,
              visitor_device=visitor_device,
              visitor_browser=browser,
              visitor_name=visitor_name)

    return