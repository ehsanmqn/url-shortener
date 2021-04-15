import uuid
from hashids import Hashids

from django.db import models
from django.utils import timezone
from django.db.models import Q, F, Count
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from django.conf import settings

from UrlShortener_auth.models import User

hashids = Hashids()

class Url(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    url = models.URLField(default='', editable=True, unique=False)
    shorten_url = models.CharField(default='', max_length=settings.SHORTEN_MAX_LENTH, editable=False, unique=True)
    created = models.DateTimeField(editable=False, db_index=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='urls')
    title = models.CharField(default='', blank=True, null=False, max_length=100)

    class Meta:
        index_together = [
            ('creator', 'uuid'),
        ]

        verbose_name = ('url')
        verbose_name_plural = ('urls')

    @classmethod
    def get_source_url_with_shorten_url(cls, shorten_url):
        return get_object_or_404(cls, shorten_url=shorten_url)

    @classmethod
    def get_url_object_for_url_with_shorten_id(cls, shorten_id):
        url = cls.objects.get(shorten_url=shorten_id)
        return url

    @classmethod
    def create_url(cls, creator, url=None, shorten_url=None , title=None, created=created):

        # ToDo: Add custom url support
        new_url = Url.objects.create(url=url, creator=creator, created=created)

        new_url.shorten_url = str(hashids.encrypt(new_url.pk));

        if title:
            new_url.title = title

        new_url.save()

        return new_url

    def update(self, url=None, title=None):
        self._check_can_be_updated(url=url)
        if title:
            # ToDo: Check for duplication
            self.title = title
        if url:
            self.url = url
        self.save()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id and not self.created:
            self.created = timezone.now()

        url = super(Url, self).save(*args, **kwargs)

        return url

    def visit(self, visitor_name, visitor_ip, visitor_device, visitor_browser):
        return UrlVisits.create_visit(visitor_name=visitor_name,
                                      visitor_device=visitor_device,
                                      visitor_ip=visitor_ip,
                                      visitor_browser=visitor_browser,
                                      url=self)

    def delete(self, *args, **kwargs):
        self.delete_media()
        super(Url, self).delete(*args, **kwargs)

    def _check_can_be_updated(self):
        if False:
            raise ValidationError(
                ('Cannot update url.')
            )

class UrlVisits(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name='visits')
    created = models.DateTimeField(editable=False)
    visitor_name = models.CharField(default='', max_length=settings.USERNAME_MAX_LENGTH)
    visitor_ip = models.GenericIPAddressField()
    visitor_device = models.IntegerField(default=1)     # 1: PC, 2: Mobile
    visitor_browser = models.CharField(default='', max_length=30)  # 1: PC, 2: Mobile

    class Meta:
        verbose_name = ('visit')
        verbose_name_plural = ('visits')

    @classmethod
    def create_visit(cls, visitor_name, visitor_ip, visitor_device, visitor_browser, url):
        return UrlVisits.objects.create(url=url, visitor_device=visitor_device,
                                        visitor_ip=visitor_ip, visitor_name=visitor_name,
                                        visitor_browser=visitor_browser)

    @classmethod
    def count_visits_for_url_with_id(cls, url_id):
        count_query = Q(url_id=url_id)

        return cls.objects.filter(count_query).count()


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(UrlVisits, self).save(*args, **kwargs)