from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.apps import apps
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Q, F, Count


from UrlShortener.settings import USERNAME_MAX_LENGTH

class User(AbstractUser):
    name = models.CharField(blank=False, null=False, max_length=100)
    email = models.EmailField(_('email address'), unique=True, null=False, blank=False)
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        blank=False,
        null=False,
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=_('Required. %(username_max_length)d characters or fewer. Letters, digits and _ only.' % {
            'username_max_length': USERNAME_MAX_LENGTH}),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with this username already exists."),
        },
    )

    phone = models.CharField(
        _('phone'),
        default='',
        blank=True,
        null=False,
        max_length=11,
        unique=True,
    )

    JWT_TOKEN_TYPE_CHANGE_EMAIL = 'CE'
    JWT_TOKEN_TYPE_PASSWORD_RESET = 'PR'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @classmethod
    def create_user(cls, username, email=None, password=None, name=None, phone=None):
        return cls.objects.create_user(username, email=email, password=password, name=name, phone=phone)

    @classmethod
    def is_email_taken(cls, email):
        try:
            cls.objects.get(email=email)
            return True
        except User.DoesNotExist:
            return False

    @classmethod
    def is_phone_taken(cls, phone):
        try:
            cls.objects.get(phone=phone)
            return True
        except User.DoesNotExist:
            return False

    def create_short_url(self, url=None, shorten_url=None, created=None):

        Url = apps.get_model('UrlShortener_urls.Url')

        url = Url.create_url(url=url, shorten_url=shorten_url, creator=self, created=created)

        return url

    def get_timeline_urls(self, count=None):

        urls_query = Q(creator_id=self.id)

        Url = apps.get_model('UrlShortener_urls.Url')
        urls = Url.objects.filter(urls_query)

        return urls

    def is_suspended(self, count=10):
        return False

    def _reset_auth_token(self):
        self.auth_token.delete()
        bootstrap_user_auth_token(user=self)

    def get_visits_for_url_with_id(self, url_id):
        Url = apps.get_model('UrlShortener_urls.Url')
        url = Url.objects.get(pk=url_id)

        return self.get_visits_for_url(url=url)

    def get_visit_analytics_for_url(self, url_id, start_time=None, end_time=None):
        Url = apps.get_model('UrlShortener_urls.Url')
        url = Url.objects.get(pk=url_id)

        if start_time:
            total_visits_query = Q(url_id=url.pk, url__creator=self, created__gte=start_time, created__lte=end_time)
        else:
            total_visits_query = Q(url_id=url.pk, url__creator=self)

        visits_by_mobile_query = total_visits_query & Q(visitor_device=2)
        visits_by_pc_query = total_visits_query & ~Q(visitor_device=2)
        visits_by_chrome_query = total_visits_query & Q(visitor_browser__startswith='Chrome')
        visits_by_firefox_query = total_visits_query & Q(visitor_browser__startswith='Firefox')

        UrlVisits = apps.get_model('UrlShortener_urls.UrlVisits')
        
        # ToDo: Use F expression in order to optimize query
        return {
            'total_visits': UrlVisits.objects.filter(total_visits_query).count(),
            'visits_by_pc': UrlVisits.objects.filter(visits_by_pc_query).count(),
            'visits_by_mobile': UrlVisits.objects.filter(visits_by_mobile_query).count(),
            'visits_by_chrome': UrlVisits.objects.filter(visits_by_chrome_query).count(),
            'visits_by_firefox': UrlVisits.objects.filter(visits_by_firefox_query).count(),
        }

    def get_visitor_analytics_for_url(self, url_id, start_time=None, end_time=None):
        Url = apps.get_model('UrlShortener_urls.Url')
        url = Url.objects.get(pk=url_id)

        if start_time:
            total_visits_query = Q(url_id=url.pk, url__creator=self, created__gte=start_time, created__lte=end_time, )
        else:
            total_visits_query = Q(url_id=url.pk, url__creator=self)

        visits_by_mobile_query = total_visits_query & Q(visitor_device=2)
        visits_by_pc_query = total_visits_query & ~Q(visitor_device=2)
        visits_by_chrome_query = total_visits_query & Q(visitor_browser__startswith='Chrome')
        visits_by_firefox_query = total_visits_query & Q(visitor_browser__startswith='Firefox')

        UrlVisits = apps.get_model('UrlShortener_urls.UrlVisits')
        
        # ToDo: Use F expression in order to optimize query
        return {
            'total_unique_visitors': UrlVisits.objects.filter(total_visits_query).values("visitor_ip").distinct().count(),
            'visitors_by_pc': UrlVisits.objects.filter(visits_by_pc_query).values("visitor_ip").distinct().count(),
            'visitors_by_mobile': UrlVisits.objects.filter(visits_by_mobile_query).values("visitor_ip").distinct().count(),
            'visitors_by_chrome': UrlVisits.objects.filter(visits_by_chrome_query).values("visitor_ip").distinct().count(),
            'visitors_by_firefox': UrlVisits.objects.filter(visits_by_firefox_query).values("visitor_ip").distinct().count(),
        }

        return UrlVisits.objects.filter(total_visits_query)

    def get_visits_for_url(self, url):
        visits_query = self._make_get_visits_for_url_query(url=url)

        UrlVisits = apps.get_model('UrlShortener_urls.UrlVisits')

        return UrlVisits.objects.filter(visits_query)

    def _make_get_visits_for_url_query(self, url):
        visits_query = Q(url_id=url.pk, url__creator=self)

        return visits_query

    def _make_visits_by_device_for_url_query(self, url):
        total_visits_query = Q(url_id=url.pk, url__creator=self)
        visits_by_pc_query = Q(visitor_device=1)
        visits_by_mobile_query = ~visits_by_pc_query

        return total_visits_query

@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid='bootstrap_auth_token')
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """"
    Create a token for all users
    """
    if created:
        bootstrap_user_auth_token(instance)

def bootstrap_user_auth_token(user):
    return Token.objects.create(user=user)
