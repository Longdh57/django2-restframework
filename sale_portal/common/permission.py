from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class PermissionIsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        return False


class PermissionNotAllow(permissions.BasePermission):
    def has_permission(self, request, view):
        return False


class PermissionAllow(permissions.BasePermission):
    def has_permission(self, request, view):
        return True


def get_user_permission_classes(permission='', request=None):
    if request is not None and request.user.is_authenticated:
        if request.user.has_perms([permission]):
            return [PermissionAllow]
    return [PermissionNotAllow]


def check_user_admin(user):
    if user.is_authenticated and user.is_superuser:
        return True
    raise PermissionDenied
