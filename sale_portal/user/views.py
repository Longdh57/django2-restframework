import json
import logging
import collections

from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, Permission
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from django.db.models import Q
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.views import JSONWebTokenAPIView
from social_core.exceptions import AuthException

from sale_portal.area.models import Area
from sale_portal.utils.permission import PermissionIsAdmin, check_user_admin
from ..user.models import CustomGroup, User
from ..user import model_names, ROLE, ROLE_SALE_MANAGER, ROLE_SALE_ADMIN
from django.http import JsonResponse
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_social_auth.views import JWTAuthMixin, BaseSocialAuthView, decorate_request
from .serializers import UserSerializer, GroupSerializer, PermissionSerializer, AccountSerializer, UserJWTSerializer
from ..staff.models import Staff
from ..common.standard_response import successful_response, custom_response, Code
from django.middleware.csrf import get_token
from django.utils import formats

from requests.exceptions import HTTPError
from django.http import HttpResponse
from social_core.utils import parse_qs


class SocialJWTUserAuthView(JWTAuthMixin, BaseSocialAuthView):
    serializer_class = UserJWTSerializer

    def post(self, request, *args, **kwargs):
        input_data = self.get_serializer_in_data()
        provider_name = self.get_provider_name(input_data)
        if not provider_name:
            return self.respond_error("Provider is not specified")
        self.set_input_data(request, input_data)
        decorate_request(request, provider_name)
        serializer_in = self.get_serializer_in(data=input_data)
        if self.oauth_v1() and request.backend.OAUTH_TOKEN_PARAMETER_NAME not in input_data:
            # oauth1 first stage (1st is get request_token, 2nd is get access_token)
            manual_redirect_uri = self.request.auth_data.pop('redirect_uri', None)
            manual_redirect_uri = self.get_redirect_uri(manual_redirect_uri)
            if manual_redirect_uri:
                self.request.backend.redirect_uri = manual_redirect_uri
            request_token = parse_qs(request.backend.set_unauthorized_token())
            return Response(request_token)
        serializer_in.is_valid(raise_exception=True)
        try:
            user = self.get_object()
        except (AuthException, HTTPError) as e:
            return self.respond_error(e)
        if isinstance(user, HttpResponse):  # An error happened and pipeline returned HttpResponse instead of user
            return user
        resp_data = self.get_serializer(instance=user)
        # self.do_login(request.backend, user)
        if user.is_active is False:
            return Response({
                'Unauthorized': 'User has been disable'
            }, status=401)
        if not user.groups.all():
            if not user.is_superuser:
                return Response({'message': 'Bạn không có bất kì nhóm quyền nào'},
                                status=status.HTTP_403_FORBIDDEN)
        elif len(user.groups.all()) > 1:
            return Response({'message': 'Bạn có nhiều hơn 1 nhóm quyền, liên hệ admin để được giải quyết'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            group = user.get_group()
            if group is None:
                return Response(
                    {'message': 'Có lỗi xảy ra với nhóm quyền của bạn. Vui lòng liên hệ Admin để được hỗ trợ'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            elif not group.status:
                return Response({
                                    'message': 'Nhóm quyền gắn với tài khoản của bạn đang tạm khóa. Vui lòng liên hệ Admin để được hỗ trợ'},
                                status=status.HTTP_403_FORBIDDEN)
        return Response(resp_data.data)


class AccountJWTUserAuthView(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            if not user.groups.all():
                if not user.is_superuser:
                    return Response({'message': 'Bạn không có bất kì nhóm quyền nào'},
                                    status=status.HTTP_403_FORBIDDEN)
            elif len(user.groups.all()) > 1:
                return Response({'message': 'Bạn có nhiều hơn 1 nhóm quyền, liên hệ admin để được giải quyết'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                group = user.get_group()
                if group is None:
                    return Response({'message': 'Có lỗi xảy ra với nhóm quyền của bạn. Vui lòng liên hệ Admin để được hỗ trợ'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                elif not group.status:
                    return Response({'message': 'Nhóm quyền gắn với tài khoản của bạn đang tạm khóa. Vui lòng liên hệ Admin để được hỗ trợ'},
                                status=status.HTTP_403_FORBIDDEN)
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


class CSRFGeneratorView(APIView):
    def get(self, request):
        csrf_token = get_token(request)
        return JsonResponse({
            'csrf_token':csrf_token
        }, status=200)


def get_user_info(user):
    user_info = {
        'is_superuser': user.is_superuser,
        'is_area_manager': user.is_area_manager,
        'is_sale_admin': user.is_sale_admin,
        'area_ids': [],
        'staff_id': None,
        'team': None,
    }

    if user.is_area_manager or user.is_sale_admin:
        areas = user.area_set.all()
        area_ids = []
        for area in areas:
            area_ids.append(area.id)
        user_info.update({'area_ids': area_ids})

    staff = Staff.objects.filter(email=user.email).first()

    if staff is not None:
        user_info.update({'staff_id': staff.id})
        team = {'id': staff.team.id, 'role': staff.role.code} if staff.team and staff.role else None

        user_info.update({'team': team})

    return user_info


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list User \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - username -- text
        - email -- text
        - status -- true/false (trạng thái)
        - role: text in { 'ADMIN', 'AREA MANAGER', 'TEAM MANAGER', 'SALE' }
    """
    serializer_class = AccountSerializer
    permission_classes = [PermissionIsAdmin]
    ordering = ['username']

    def get_queryset(self):
        queryset = User.objects.all()

        username = self.request.query_params.get('username', None)
        email = self.request.query_params.get('email', None)
        status = self.request.query_params.get('status', None)
        role = self.request.query_params.get('role', None)

        if username is not None and username != '':
            queryset = queryset.filter(username__icontains=username)
        if email is not None and email != '':
            queryset = queryset.filter(email__icontains=email)
        if status is not None and status != '':
            status = True if status == 'true' else False
            queryset = queryset.filter(is_active=status)
        if role is not None and role != '':
            role = role.upper()
            # ROLE ADMIN
            if role == ROLE[0]:
                queryset = queryset.filter(is_superuser=True)
            # ROLE OTHER
            elif role == ROLE[1]:
                staff_emails = Staff.objects.all().values('email')
                queryset = queryset.filter(is_superuser=False).filter(groups__isnull=True)
            else:
                queryset = queryset.filter(groups__name=role)

        return queryset

    def retrieve(self, request, pk):
        """
            API get detail user
        """
        user = User.objects.filter(pk=pk).first()
        if user is None:
            return custom_response(Code.USER_NOT_FOUND)

        user_permissions = user.user_permissions.all()
        group_permissions = Permission.objects.filter(group__user=user).all()

        data = {
            'user': AccountSerializer(user).data,
            'user_permissions': PermissionSerializer(user_permissions, many=True).data,
            'group_permissions': PermissionSerializer(group_permissions, many=True).data,
        }

        return successful_response(data)

    def update(self, request, pk):
        """
            API update user info \n
            Request body for this api : Không được bỏ trống \n
                {
                    "is_active": boolean true/false,
                    "role_name": text,
                    "area_ids": [1,2..],
                    "user_permissions": [1,2,3,4,5,6...],
                }
        """
        user = User.objects.filter(pk=pk).first()
        if user is None:
            return custom_response(Code.USER_NOT_FOUND)

        try:
            body = json.loads(request.body)

            is_active = body.get('is_active')
            role_name = body.get('role_name')
            area_ids = body.get('area_ids')
            user_permissions = body.get('user_permissions')

            if user_permissions is None or not isinstance(user_permissions, list):
                return custom_response(Code.INVALID_BODY, 'List user-permission not valid')
            if Permission.objects.filter(pk__in=user_permissions).count() != len(user_permissions):
                return custom_response(Code.PERMISSION_NOT_FOUND)

            old_role_name = user.get_role_name()
            if role_name is not None and role_name != '' and old_role_name != role_name.upper():
                role_name = role_name.upper()
                if role_name == ROLE[0]:
                    user.groups.clear()
                    user.is_superuser = True
                else:
                    group = Group.objects.filter(name=role_name)
                    if not group:
                        return custom_response(Code.INVALID_BODY, 'group_name not valid')
                    else:
                        if role_name == ROLE_SALE_MANAGER or role_name == ROLE_SALE_ADMIN:
                            if not area_ids or not isinstance(area_ids, list):
                                return custom_response(Code.INVALID_BODY, 'List Area not valid')
                            if Area.objects.filter(pk__in=area_ids).count() != len(area_ids):
                                return custom_response(Code.AREA_NOT_FOUND)
                            user.area_set.clear()
                            user.area_set.set(area_ids)
                            if role_name == ROLE_SALE_MANAGER:
                                user.is_area_manager = True
                            else:
                                user.is_sale_admin = True

                        user.groups.set(group)

                if old_role_name == ROLE[0]:
                    user.is_superuser = False
                if old_role_name == ROLE_SALE_MANAGER:
                    user.is_area_manager = False
                    if role_name != ROLE_SALE_ADMIN:
                        user.area_set.clear()
                if old_role_name == ROLE_SALE_ADMIN:
                    user.is_sale_admin = False
                    if role_name != ROLE_SALE_MANAGER:
                        user.area_set.clear()

            user.is_active = (is_active == 'true')
            user.save()
            user.user_permissions.set(user_permissions)

            return successful_response()

        except Exception as e:
            logging.error('Create team exception: %s', e)
            print(e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)


class GroupViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
        API get list group_permission \n
    """
    serializer_class = GroupSerializer
    permission_classes = [PermissionIsAdmin]
    ordering = ['-id']

    def get_queryset(self):
        queryset = CustomGroup.objects.all()

        group_id = self.request.query_params.get('group_id', None)
        status = self.request.query_params.get('status', None)

        if group_id is not None and group_id != '':
            queryset = queryset.filter(pk=group_id)

        if status is not None and status != '':
            status = True if status == 'true' else False
            queryset = queryset.filter(status=status)

        return queryset

    def create(self, request):
        """
            API create account_group_permission\n
            Request body for this api : Không được bỏ trống \n
                {
                    'group_name' : 'text',
                    'group_permissions' : [1,2,3,4,5,6..]
                }
        """
        try:
            body = json.loads(request.body)
            group_name = None
            group_permissions = []
            if 'group_name' in body:
                group_name = body['group_name']
            if 'group_permissions' in body:
                group_permissions = body['group_permissions']

            if group_name is None or group_name == '':
                return custom_response(Code.INVALID_BODY, 'group_name not valid')

            if Group.objects.filter(name__iexact=group_name):
                return custom_response(Code.BAD_REQUEST, 'Group_name have been used')

            custom_group = CustomGroup(
                name=group_name.upper(),
                created_by=request.user,
                updated_by=request.user
            )
            custom_group.save()
            custom_group.permissions.set(group_permissions)
            custom_group.save()

            return successful_response(custom_group.id)
        except Exception as e:
            logging.error('Create account_group_permission exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        """
            API get detail account_group_permission
        """
        custom_group = CustomGroup.objects.filter(pk=pk).first()
        if custom_group is None:
            return custom_response(Code.GROUP_NOT_FOUND)

        permissions = []

        for permission in custom_group.permissions.all():
            element = {
                'id': permission.id,
                'name': permission.name,
                'codename': permission.codename,
                'content_type': {
                    'id': permission.content_type.id,
                    'model': permission.content_type.model
                }
            }
            permissions.append(element)

        data = {
            'id': custom_group.id,
            'name': custom_group.name,
            'status': custom_group.status,
            'created_date': formats.date_format(custom_group.created_date, "SHORT_DATETIME_FORMAT") if custom_group.created_date else '',
            'created_by': custom_group.created_by.username if custom_group.created_by else '',
            'updated_date': formats.date_format(custom_group.updated_date, "SHORT_DATETIME_FORMAT") if custom_group.updated_date else '',
            'updated_by': custom_group.updated_by.username if custom_group.updated_by else '',
            'permissions': permissions
        }

        return successful_response(data)

    def update(self, request, pk):
        """
            API update account_group_permission\n
            Request body for this api : Không được bỏ trống \n
                {
                    'status': true/false
                    'group_permissions' : [1,2,3,4,5,6..]
                }
        """
        try:
            custom_group = CustomGroup.objects.filter(pk=pk).first()
            if custom_group is None:
                return custom_response(Code.GROUP_NOT_FOUND)

            body = json.loads(request.body)
            status = None
            group_permissions = []
            if 'status' in body:
                status = body['status']
            if 'group_permissions' in body:
                group_permissions = body['group_permissions']

            if status is None or status == '':
                return custom_response(Code.INVALID_BODY, 'Status not valid')

            status = True if status == 'true' else False

            custom_group.status = status
            custom_group.updated_by = request.user
            custom_group.permissions.clear()
            custom_group.permissions.set(group_permissions)
            custom_group.save()

            return successful_response()
        except Exception as e:
            logging.error('Delete account_group_permission exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@login_required
@user_passes_test(check_user_admin)
def list_groups(request):
    """
        API get list Groups to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
    """

    queryset = CustomGroup.objects.all()

    name = request.GET.get('name', None)

    if name is not None and name != '':
        queryset = queryset.filter(name__icontains=name)

    queryset = queryset.order_by('name')[0:settings.PAGINATE_BY]

    data = [{'id': custom_group.id, 'name': custom_group.name} for custom_group in queryset]

    return successful_response(data)


class PermissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list Permissions \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
    """
    serializer_class = PermissionSerializer
    permission_classes = [PermissionIsAdmin]
    ordering = ['codename']

    def get_queryset(self):
        queryset = Permission.objects.all()

        name = self.request.query_params.get('name', None)

        if name is not None and name != '':
            queryset = queryset.filter(Q(name__icontains=name) | Q(codename__icontains=name))

        return queryset


@api_view(['GET'])
@login_required
@user_passes_test(check_user_admin)
def model_permissions(request):
    """
        API get list model-permissions \n
    """

    queryset = Permission.objects.all().order_by('id')

    model_permissions = dict()

    for permission in queryset:
        if permission.content_type.model not in model_names:
            continue
        item = {
            'id': permission.id,
            'name': permission.name,
            'codename': permission.codename
        }
        if permission.content_type.model in model_permissions:
            permissions = model_permissions[permission.content_type.model]
        else:
            permissions = []
        permissions.append(item)
        model_permissions[permission.content_type.model] = permissions

    return successful_response(collections.OrderedDict(sorted(model_permissions.items())))
