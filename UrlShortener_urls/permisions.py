from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from django.utils.translation import ugettext_lazy as _
from django.contrib.humanize.templatetags.humanize import naturaltime

class IsGetOrIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        # allow all GET requests
        if request.method == 'GET':
            return True

        # Otherwise, only allow authenticated requests
        # Post Django 1.10, 'is_authenticated' is a read-only attribute
        return request.user and request.user.is_authenticated

class IsNotSuspended(BasePermission):
    """
    Dont allow access to suspended users
    """

    def has_permission(self, request, view):
        user = request.user
        return check_user_is_not_suspended(user=user)


def check_user_is_not_suspended(user):
    if not user.is_anonymous:
        is_suspended = user.is_suspended()
        if is_suspended:
            longest_suspension = user.get_longest_moderation_suspension()

            raise PermissionDenied(
                _('Your account has been suspended and will be unsuspended in %s' % naturaltime(
                    longest_suspension.expiration)))

    return True