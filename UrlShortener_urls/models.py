import uuid
from hashids import Hashids

from django.db import models

from UrlShortener_auth.models import User
from UrlShortener import settings

hashids = Hashids()

class Url(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    url = models.URLField(default='', editable=True, unique=False)
    shorten_url = models.CharField(default='', max_length=settings.SHORTEN_MAX_LENTH, editable=False, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='urls')
    title = models.CharField(default='', blank=True, null=False, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = [
            ('creator', 'uuid'),
        ]

        verbose_name = ('url')
        verbose_name_plural = ('urls')

    @classmethod
    def get_source_url_with_shorten_url(cls, shorten_url):
        try:
            url = cls.objects.get(shorten_url=shorten_url)
            return url.url
        except:
            return None

    @classmethod
    def get_url_object_for_url_with_shorten_id(cls, shorten_id):
        url = cls.objects.get(shorten_url=shorten_id)
        return url

    @classmethod
    def create_url(cls, creator, url=None, shorten_url=None , title=None):

        new_url = Url.objects.create(url=url, creator=creator)

        new_url.shorten_url = str(hashids.encrypt(new_url.pk))

        if title:
            new_url.title = title

        # # ToDo: Check duplicate conditions for shorten_url
        if shorten_url:
            new_url.shorten_url = shorten_url

        new_url.save()

        return new_url

    def visit(self, visitor_name, visitor_ip, visitor_device, visitor_browser):
        return Visit.create_visit(visitor_name=visitor_name,
                                  visitor_device=visitor_device,
                                  visitor_ip=visitor_ip,
                                  visitor_browser=visitor_browser,
                                  url=self)


class Visit(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name='visits')
    visitor_name = models.CharField(default='', max_length=settings.USERNAME_MAX_LENGTH)
    visitor_ip = models.GenericIPAddressField()
    visitor_device = models.CharField(default='', max_length=30)
    visitor_browser = models.CharField(default='', max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ('visit')
        verbose_name_plural = ('visits')

    @classmethod
    def create_visit(cls, visitor_name, visitor_ip, visitor_device, visitor_browser, url):
        return cls.objects.create(url=url, visitor_device=visitor_device,
                                    visitor_ip=visitor_ip, visitor_name=visitor_name,
                                    visitor_browser=visitor_browser)


class Analytics(models.Model):
    # url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name='analytics')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    total_visit = models.PositiveIntegerField(default=0)
    desktop_visit = models.PositiveIntegerField(default=0)
    mobile_visit = models.PositiveIntegerField(default=0)
    other_devices_visit = models.PositiveIntegerField(default=0)
    chrome_visit = models.PositiveIntegerField(default=0)
    firefox_visit = models.PositiveIntegerField(default=0)
    other_explorers_visit = models.PositiveIntegerField(default=0)

    unique_visitor = models.PositiveIntegerField(default=0)
    unique_desktop_visitor = models.PositiveIntegerField(default=0)
    unique_mobile_visitor = models.PositiveIntegerField(default=0)
    unique_other_devices_visitor = models.PositiveIntegerField(default=0)
    unique_chrome_visitor = models.PositiveIntegerField(default=0)
    unique_firefox_visitor = models.PositiveIntegerField(default=0)
    unique_other_explorers_visitor = models.PositiveIntegerField(default=0)

    created_at = models.TimeField(auto_now_add=True)

    class Meta:
        verbose_name = ('analytics')
        verbose_name_plural = ('analytics')

    @classmethod
    def create_analytics(cls, url):
        pass