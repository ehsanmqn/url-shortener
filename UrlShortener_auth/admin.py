from django.contrib import admin

from UrlShortener_auth.models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ('username',)

    exclude = ('password',)

    list_display = (
        'email',
        'phone',
    )

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

admin.site.register(User, UserAdmin)