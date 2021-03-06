import json
import logging
import collections

from datetime import datetime
from django.db.models import Q
from django.utils import formats
from django.conf import settings
from rest_framework import status
from social_core.utils import parse_qs
from rest_framework.views import APIView
from requests.exceptions import HTTPError
from rest_framework import viewsets, mixins
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView
from django.contrib.auth.models import Group, Permission
from social_core.exceptions import AuthException, AuthForbidden
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_social_auth.views import JWTAuthMixin, BaseSocialAuthView, decorate_request

from sale_portal.team.models import Team
from sale_portal.area.models import Area
from sale_portal.staff.models import Staff
from sale_portal.user.models import CustomGroup, User
from sale_portal.utils.permission import PermissionIsAdmin, check_user_admin
from sale_portal.common.standard_response import successful_response, custom_response, Code
from sale_portal.user import model_names, ROLE_SALE_MANAGER, ROLE_SALE_ADMIN, ROLE_ADMIN, ROLE_OTHER, ROLE_SALE_LEADER, \
    ROLE_SALE
from sale_portal.user.serializers import UserSerializer, GroupSerializer, PermissionSerializer, AccountSerializer, \
    UserJWTSerializer


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
            if isinstance(e, AuthForbidden):
                return Response({
                    'message': 'T??i kho???n ????ng nh???p kh??ng ph???i VNPAY, TRIPI or TEKO.'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'message': '????ng nh???p th???t b???i!'
            }, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(user, HttpResponse):  # An error happened and pipeline returned HttpResponse instead of user
            return user
        resp_data = self.get_serializer(instance=user)
        # self.do_login(request.backend, user)
        if user.is_active is False:
            return Response({
                'message': 'T??i kho???n ???? b??? kh??a, vui l??ng li??n h??? admin ????? ???????c h??? tr???.'
            }, status=status.HTTP_400_BAD_REQUEST)
        if not user.groups.all():
            if not user.is_superuser:
                return Response({'message': 'B???n kh??ng c?? b???t k?? nh??m quy???n n??o'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif len(user.groups.all()) > 1:
            return Response({'message': 'B???n c?? nhi???u h??n 1 nh??m quy???n, li??n h??? admin ????? ???????c gi???i quy???t'},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            group = user.get_group()
            if group is None:
                return Response(
                    {'message': 'C?? l???i x???y ra v???i nh??m quy???n c???a b???n. Vui l??ng li??n h??? Admin ????? ???????c h??? tr???'},
                    status=status.HTTP_400_BAD_REQUEST)
            elif not group.status:
                return Response({
                    'message': 'Nh??m quy???n g???n v???i t??i kho???n c???a b???n ??ang t???m kh??a. Vui l??ng li??n h??? Admin ????? ???????c h??? tr???'},
                    status=status.HTTP_400_BAD_REQUEST)
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
                    return Response({'message': 'B???n kh??ng c?? b???t k?? nh??m quy???n n??o'},
                                    status=status.HTTP_400_BAD_REQUEST)
            elif len(user.groups.all()) > 1:
                return Response({'message': 'B???n c?? nhi???u h??n 1 nh??m quy???n, li??n h??? admin ????? ???????c gi???i quy???t'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                group = user.get_group()
                if group is None:
                    return Response(
                        {'message': 'C?? l???i x???y ra v???i nh??m quy???n c???a b???n. Vui l??ng li??n h??? Admin ????? ???????c h??? tr???'},
                        status=status.HTTP_400_BAD_REQUEST)
                elif not group.status:
                    return Response({
                                        'message': 'Nh??m quy???n g???n v???i t??i kho???n c???a b???n ??ang t???m kh??a. Vui l??ng li??n h??? Admin ????? ???????c h??? tr???'},
                                    status=status.HTTP_400_BAD_REQUEST)
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

        message = serializer.errors['non_field_errors'][0]
        if message == 'Unable to log in with provided credentials.':
            message = 'Sai t??n truy c???p ho???c m???t kh???u.'
        if message == 'User account is disabled.':
            message = 'T??i kho???n ???? b??? kh??a, vui l??ng li??n h??? admin ????? ???????c h??? tr???.'

        return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


class CSRFGeneratorView(APIView):
    def get(self, request):
        csrf_token = get_token(request)
        return JsonResponse({
            'csrf_token': csrf_token
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
        team = {'id': staff.team.id, 'role': staff.role} if staff.team else None

        user_info.update({'team': team})

    return user_info


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list User \n
        Parameters for this api : C?? th??? b??? tr???ng ho???c kh??ng g???i l??n
        - username -- text
        - email -- text
        - status -- true/false (tr???ng th??i)
        - role: text in { 'ADMIN', 'SALE MANAGER', 'SALE ADMIN', 'SALE LEADER', 'SALE', 'OTHER' }
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
            if role == ROLE_ADMIN:
                queryset = queryset.filter(is_superuser=True)
            elif role == ROLE_OTHER:
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

        areas, teams = [], []

        for item in user.area_set.all():
            area = {
                'id': item.id,
                'name': item.name,
                'code': item.code
            }
            areas.append(area)

        for item in user.team_set.all():
            team = {
                'id': item.id,
                'name': item.name,
                'code': item.code
            }
            teams.append(team)

        data = {
            'user': AccountSerializer(user).data,
            'areas': areas,
            'teams': teams,
            'user_permissions': PermissionSerializer(user_permissions, many=True).data,
            'group_permissions': PermissionSerializer(group_permissions, many=True).data,
        }

        return successful_response(data)

    def update(self, request, pk):
        """
            API update user info \n
            Request body for this api : Kh??ng ???????c b??? tr???ng \n
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
            is_manager_outside_vnpay = body.get('is_manager_outside_vnpay')
            role_name = body.get('role_name')
            area_ids = body.get('area_ids')
            team_ids = body.get('team_ids')
            user_permissions = body.get('user_permissions')

            if is_active is None or is_active not in ['true', 'false']:
                return custom_response(Code.INVALID_BODY, 'Field is_active not valid')

            if is_manager_outside_vnpay is None or is_manager_outside_vnpay not in ['true', 'false']:
                return custom_response(Code.INVALID_BODY, 'Field is_manager_outside_vnpay not valid')

            if role_name is None or role_name == '' or not isinstance(role_name, str):
                return custom_response(Code.INVALID_BODY, 'Field role_name not valid')

            role_name = role_name.upper()

            # Admin
            if role_name == ROLE_ADMIN:
                user.groups.clear()
                user.area_set.clear()
                user.user_permissions.clear()
                user.is_superuser = True
                user.is_area_manager = False
                user.is_sale_admin = False
                user.is_active = (is_active == 'true')
                user.save()
                return successful_response()

            # validate list permission
            if user_permissions is None or not isinstance(user_permissions, list):
                return custom_response(Code.INVALID_BODY, 'List user-permission not valid')
            if Permission.objects.filter(pk__in=user_permissions).count() != len(user_permissions):
                return custom_response(Code.PERMISSION_NOT_FOUND)

            group = Group.objects.filter(name=role_name)
            if not group:
                return custom_response(Code.GROUP_NOT_FOUND)

            if role_name == ROLE_SALE_MANAGER or role_name == ROLE_SALE_ADMIN:
                if user.is_manager_outside_vnpay or (is_manager_outside_vnpay == 'true'):
                    # Check ?????nh d???ng team_ids n???u role l?? ROLE_SALE_MANAGER / ROLE_SALE_ADMIN v?? l?? ng?????i Tripi, Teko
                    if not isinstance(team_ids, list):
                        return custom_response(Code.INVALID_BODY, 'List Team not valid')
                    if Team.objects.filter(pk__in=team_ids).count() != len(team_ids):
                        return custom_response(Code.TEAM_NOT_FOUND)
                    user.team_set.set(team_ids)
                else:
                    # Check ?????nh d???ng area_ids n???u role l?? ROLE_SALE_MANAGER / ROLE_SALE_ADMIN v?? l?? ng?????i VNpay
                    if not isinstance(area_ids, list):
                        return custom_response(Code.INVALID_BODY, 'List Area not valid')
                    if Area.objects.filter(pk__in=area_ids).count() != len(area_ids):
                        return custom_response(Code.AREA_NOT_FOUND)
                    user.area_set.set(area_ids)

                user.groups.set(group)
                user.is_superuser = False
                user.is_area_manager = True if role_name == ROLE_SALE_MANAGER else False
                user.is_sale_admin = True if role_name == ROLE_SALE_ADMIN else False

            if role_name == ROLE_SALE_LEADER or role_name == ROLE_SALE:
                user.groups.set(group)
                user.area_set.clear()
                user.is_superuser = False
                user.is_area_manager = False
                user.is_sale_admin = False

            user.is_manager_outside_vnpay = (is_manager_outside_vnpay == 'true')
            user.is_active = (is_active == 'true')
            user.save()
            user.user_permissions.set(user_permissions)

            return successful_response()

        except Exception as e:
            logging.error('Update team exception: %s', e)
            print(e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@login_required
def user_info(request):
    """
        API get user information \n
    """

    user = request.user

    if user is None:
        return custom_response(Code.PERMISSION_DENIED)

    return successful_response(UserSerializer(user).data)


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
            Request body for this api : Kh??ng ???????c b??? tr???ng \n
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
            'created_date': formats.date_format(custom_group.created_date,
                                                "SHORT_DATETIME_FORMAT") if custom_group.created_date else '',
            'created_by': custom_group.created_by.username if custom_group.created_by else '',
            'updated_date': formats.date_format(custom_group.updated_date,
                                                "SHORT_DATETIME_FORMAT") if custom_group.updated_date else '',
            'updated_by': custom_group.updated_by.username if custom_group.updated_by else '',
            'permissions': permissions
        }

        return successful_response(data)

    def update(self, request, pk):
        """
            API update account_group_permission\n
            Request body for this api : Kh??ng ???????c b??? tr???ng \n
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
        Parameters for this api : C?? th??? b??? tr???ng ho???c kh??ng g???i l??n
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
        Parameters for this api : C?? th??? b??? tr???ng ho???c kh??ng g???i l??n
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
        print(f'Permission: {permission.id}')
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


def update_role_for_staff(staff_ids=[], role_name=''):
    try:
        group = Group.objects.filter(name=role_name)
        if not group:
            return False
        emails = Staff.objects.filter(pk__in=staff_ids).values('email')
        users = User.objects.filter(email__in=emails).exclude(groups__name=role_name)

        for user in users:
            user.groups.set(group)
            user.area_set.clear()
            user.is_superuser = False
            user.is_area_manager = False
            user.is_sale_admin = False
            user.save()

        return True
    except Exception as e:
        logging.error(e)
        return False
