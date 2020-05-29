from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url


from UrlShortener_auth.views import Register, Login
from UrlShortener_urls.views import Urls, RedirectToLongURL, UrlVisits, UrlVisitAnalytics, UrlVisitorAnalytics

admin.site.site_header = "UrlShortener Url Shortener Administration Site"
admin.site.site_title = "Portal"
admin.site.index_title = "UrlShortener Admin"

auth_patterns = [
    path('register/', Register.as_view(), name='register-user'),
    path('login/', Login.as_view(), name='login-user'),
]

analytics_patterns = [
    path('visitor/', UrlVisitorAnalytics.as_view(), name='url-visitor-analytics'),
    path('visit', UrlVisitAnalytics.as_view(), name='url-visit-analytics')
]

url_patterns = [
    path('', Urls.as_view(), name='create-url'),
    path('visit/', UrlVisits.as_view(), name='url-visits'),
    path('analytics/', include(analytics_patterns))
]

api_patterns = [
    path('auth/', include(auth_patterns)),
    path('url/', include(url_patterns)),
]

redirect_pattern = [
    path(r'^(?P<id>[a-zA-Z0-9])$', Urls.as_view()),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
    re_path(r'^r/(?P<short_url>\w+)/$', RedirectToLongURL, name='redirec-to-source-url')
]
