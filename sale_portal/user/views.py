import json
import logging
import collections

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from django.db.models import Q
from social_core.exceptions import AuthException

from ..user.models import CustomGroup, User
from ..user.serializers import ROLE
from ..user import model_names
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_social_auth.views import JWTAuthMixin, BaseSocialAuthView, decorate_request
from rest_social_auth.serializers import JWTSerializer
from .serializers import UserSerializer, GroupSerializer, PermissionSerializer, UserListViewSerializer
from ..staff.models import Staff
from ..staff import StaffTeamRoleType
from ..common.standard_response import successful_response, custom_response, Code
from django.middleware.csrf import get_token
from django.utils import formats

from requests.exceptions import HTTPError
from django.http import HttpResponse
from social_core.utils import parse_qs


class UserJWTSerializer(JWTSerializer, UserSerializer):
    pass


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
                'Unauthorized': 'User have been disable'
            }, status=401)
        return Response(resp_data.data)


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
        'team_area_ids': [],
        'staff_id': None,
        'team': None,
    }

    if user.is_area_manager:
        teams = user.team_set.all()
        team_ids = []
        for team in teams:
            team_ids.append(team.id)
        user_info.update({'team_area_ids': team_ids})

    staff = Staff.objects.filter(email=user.email).first()

    if staff is not None:
        user_info.update({'staff_id': staff.id})
        team = {'id': staff.team.id, 'role': staff.role.code} if staff.team and staff.role else None

        user_info.update({'team': team})

    return user_info


def get_staffs_viewable(user):
    staff_ids = []

    if not user.is_superuser:
        team_ids = []
        staff_id = None
        if user.is_area_manager:
            teams = user.team_set.all()
            for team in teams:
                team_ids.append(team.id)
        else:
            staff = Staff.objects.filter(email=user.email).first()
            if staff.team and staff.role and staff.role.code == \
                    StaffTeamRoleType.CHOICES[StaffTeamRoleType.TEAM_MANAGEMENT][1]:
                team_ids.append(staff.team.id)
            else:
                staff_id = staff.id

        if team_ids:
            staffs = Staff.objects.filter(team__in=team_ids).values('id')
            for staff in staffs:
                staff_ids.append(staff.id)
        else:
            staff_ids.append(staff_id)

    return staff_ids


class PermissionIsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        return False


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list User \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - username -- text
        - email -- text
        - status -- true/false (trạng thái)
        - role: text in { 'ADMIN', 'AREA MANAGER', 'TEAM MANAGER', 'SALE' }
    """
    serializer_class = UserListViewSerializer
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
            if role in ROLE.values():
                if role == ROLE[0]:
                    queryset = queryset.filter(is_superuser=True)
                if role == ROLE[1]:
                    queryset = queryset.filter(is_area_manager=True)
                if role == ROLE[2]:
                    queryset = queryset.filter(is_sale_admin=True)
                if role == ROLE[3]:
                    staff_emails = Staff.objects.filter(role__code__iexact='TEAM_MANAGEMENT').values('email')
                    queryset = queryset.filter(email__in=staff_emails, is_superuser=False,
                                               is_area_manager=False, is_sale_admin=False)
                if role == ROLE[4]:
                    staff_emails = Staff.objects.exclude(role__code__iexact='TEAM_MANAGEMENT').values('email')
                    queryset = queryset.filter(email__in=staff_emails, is_superuser=False,
                                               is_area_manager=False, is_sale_admin=False)
                if role == ROLE[5]:
                    staff_emails = Staff.objects.all().values('email')
                    queryset = queryset.filter(is_superuser=False, is_area_manager=False,
                                               is_sale_admin=False).exclude(email__in=staff_emails)
            else:
                queryset = User.objects.none()

        return queryset


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
                name=group_name,
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
