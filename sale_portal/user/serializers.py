from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, ContentType
from ..user.models import CustomGroup
from django.utils import formats

from sale_portal.staff.models import Staff

ROLE = {
    0: 'ADMIN',
    1: 'OTHER',
}


class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    def get_permissions(self, user):
        permissions = []
        for x in Permission.objects.filter(Q(user=user) | Q(group__user=user)).all():
            permissions.append(x.codename)
        return permissions

    def get_role(self, user):
        if user.is_superuser:
            return ROLE[0]
        group = user.groups.first()
        if group is None:
            return ROLE[1]
        return group.name

    class Meta:
        model = get_user_model()
        exclude = (
            'password', 'last_login', 'groups', 'is_staff', 'send_disable_shop_email', 'user_permissions'
        )


class UserListViewSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, user):
        if user.is_superuser:
            return ROLE[0]
        if user.is_area_manager:
            return ROLE[1]
        if user.is_sale_admin:
            return ROLE[2]
        else:
            staff = Staff.objects.filter(email=user.email).order_by('id').first()
            if staff is not None:
                if staff.role is not None and staff.role.code == 'TEAM_MANAGEMENT':
                    return ROLE[3]
                return ROLE[4]
            return ROLE[5]

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'last_login',
                  'role')


class GroupSerializer(serializers.ModelSerializer):
    created_date = serializers.SerializerMethodField()
    updated_date = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    def get_created_date(self, custom_group):
        return formats.date_format(custom_group.created_date, "SHORT_DATETIME_FORMAT") if custom_group.created_date else ''

    def get_updated_date(self, custom_group):
        return formats.date_format(custom_group.updated_date, "SHORT_DATETIME_FORMAT") if custom_group.updated_date else ''

    def get_created_by(self, custom_group):
        return custom_group.created_by.username if custom_group.created_by else ''

    def get_updated_by(self, custom_group):
        return custom_group.updated_by.username if custom_group.updated_by else ''

    class Meta:
        model = CustomGroup
        fields = (
            'id', 'name', 'status', 'created_date', 'updated_date', 'created_by', 'updated_by'
        )


class ContentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = (
            'app_label', 'model'
        )


class PermissionSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer()

    class Meta:
        model = Permission
        fields = (
            'id', 'name', 'codename', 'content_type'
        )
