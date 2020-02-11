from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, ContentType
from rest_social_auth.serializers import JWTSerializer

from ..user.models import CustomGroup
from django.utils import formats


class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    def get_permissions(self, user):
        permissions = []
        for x in Permission.objects.filter(Q(user=user) | Q(group__user=user)).all().distinct():
            permissions.append(x.codename)
        return permissions

    def get_role(self, user):
        return user.get_role_name()

    class Meta:
        model = get_user_model()
        exclude = (
            'password', 'last_login', 'groups', 'is_staff', 'send_disable_shop_email', 'user_permissions'
        )


class UserJWTSerializer(JWTSerializer, UserSerializer):
    pass


class AccountSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, user):
        return user.get_role_name()

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
