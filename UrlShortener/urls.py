from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url

from UrlShortener_auth.views import Register, Login
from UrlShortener_urls.views import UrlView, RedirectToLongURL, RetrieveUrlVisitAnalytics

admin.site.site_header = "UrlShortener Url Shortener Administration Site"
admin.site.site_title = "Portal"
admin.site.index_title = "UrlShortener Admin"

auth_patterns = [
    path('register/', Register.as_view(), name='register-user'),
    path('login/', Login.as_view(), name='login-user'),
]

url_patterns = [
    path('', UrlView.as_view(), name='url-view'),
    url(r'^(?P<pk>\d+)/analytics/(?P<days>\d+)/$', RetrieveUrlVisitAnalytics.as_view(), name='retrieve-url-analytics'),
]

version1_patterns = [
    path('auth/', include(auth_patterns)),
    path('url/', include(url_patterns)),
]

api_patterns = [
    path('v1/', include(version1_patterns), name='version-1')
]

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(api_patterns)),

    re_path(r'^r/(?P<hash>\w+)/$', RedirectToLongURL, name='redirect-to-source-url')
]
