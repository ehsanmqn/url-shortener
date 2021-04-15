from django.contrib import admin

from UrlShortener_urls.models import Url, Visit


class UrlAdmin(admin.ModelAdmin):
    search_fields = ('url', 'shorten_url')

    list_display = (
        'url',
        'uuid',
        'shorten_url',
        'creator',
        'created_at'
    )

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

class UrlVisitAdmin(admin.ModelAdmin):
    search_fields = ('url', 'visitor_name', 'visitor_ip')

    list_display = (
        'url',
        'visitor_name',
        'visitor_ip',
        'visitor_device',
        'visitor_browser',
        'created_at'
    )

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

admin.site.register(Url, UrlAdmin)
admin.site.register(Visit, UrlVisitAdmin)