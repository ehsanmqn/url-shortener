from django.contrib import admin

from UrlShortener_urls.models import Url, Visit, Analytics


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

class AnalyticsAdmin(admin.ModelAdmin):
    search_fields = ('uuid',)

    list_display = (
        'id',
        'uuid',
        'total_visit',
        # 'desktop_visit',
        # 'mobile_visit',
        # 'chrome_visit',
        # 'firefox_visit',
        'unique_visitor',
        # 'unique_desktop_visitor',
        # 'unique_mobile_visitor',
        # 'unique_chrome_visitor',
        # 'unique_firefox_visitor'
    )

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True


admin.site.register(Url, UrlAdmin)
admin.site.register(Visit, UrlVisitAdmin)
admin.site.register(Analytics, AnalyticsAdmin)