from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, ContentType
from ..user.models import CustomGroup
from django.utils import formats

from sale_portal.staff.models import Staff

ROLE = {
    0: 'AREA MANAGER',
    1: 'TEAM MANAGER',
    2: 'SALE',
    3: 'OTHER',
    4: 'admin',
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
            return ROLE[4]
        if user.is_area_manager:
            return ROLE[0]
        else:
            staff = Staff.objects.filter(email=user.email).order_by('id').first()
            if staff is not None:
                return ROLE[2]
            return ROLE[3]

    class Meta:
        model = get_user_model()
        exclude = (
            'password', 'last_login', 'groups', 'is_staff', 'send_disable_shop_email', 'user_permissions'
        )


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
