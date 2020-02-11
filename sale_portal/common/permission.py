from rest_framework import permissions


class PermissionDenied(permissions.BasePermission):
    def has_permission(self, request, view):
        return False


class PermissionAllow(permissions.BasePermission):
    def has_permission(self, request, view):
        return True


def get_user_permission_classes(permission='', request=None):
    if request.user.is_authenticated:
        if request.user.has_perms([permission]):
            return [PermissionAllow]
    return [PermissionDenied]