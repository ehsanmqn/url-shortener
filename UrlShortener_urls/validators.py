from rest_framework.exceptions import ValidationError, NotFound
from django.utils.translation import ugettext_lazy as _

from UrlShortener_urls.models import Url, UrlVisits

SORT_CHOICES = ['ASC', 'DESC']

def url_uuid_exists(url_uuid):
    if not Url.objects.filter(uuid=url_uuid).exists():
        raise NotFound(
            _('The url does not exist.'),
        )