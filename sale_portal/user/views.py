import json
import logging
from django.contrib.auth.models import Group
from rest_framework import permissions
from rest_framework import viewsets, mixins
from .serializers import UserSerializer, GroupSerializer
from ..staff.models import Staff
from ..staff import StaffTeamRoleType
from ..common.standard_response import successful_response, custom_response, Code


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


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
            if staff.team and staff.role and staff.role.code == StaffTeamRoleType.CHOICES[StaffTeamRoleType.TEAM_MANAGEMENT][1]:
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


class GroupViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
        API get list group_permission \n
    """
    serializer_class = GroupSerializer
    permission_classes = [PermissionIsAdmin]
    ordering = ['-id']

    def get_queryset(self):
        queryset = Group.objects.all()
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

            group = Group.objects.filter(name__iexact=group_name)
            if group:
                return custom_response(Code.BAD_REQUEST, 'Group_name have been used')
            group = Group.objects.create(name=group_name)
            group.permissions.set(group_permissions)
            group.save()

            return successful_response(group.id)
        except Exception as e:
            logging.error('Create account_group_permission exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        """
            API get detail account_group_permission
        """
        group = Group.objects.filter(pk=pk).first()
        if group is None:
            return custom_response(Code.GROUP_NOT_FOUND)

        permissions = []

        for permission in group.permissions.all():
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
            'id': group.id,
            'name': group.name,
            'permissions': permissions
        }

        return successful_response(data)

    def update(self, request, pk):
        """
            API update account_group_permission\n
            Request body for this api : Không được bỏ trống \n
                {
                    'group_name' : 'text',
                    'group_permissions' : [1,2,3,4,5,6..]
                }
        """
        try:
            group = Group.objects.filter(pk=pk).first()
            if group is None:
                return custom_response(Code.GROUP_NOT_FOUND)

            body = json.loads(request.body)
            group_name = None
            group_permissions = []
            if 'group_name' in body:
                group_name = body['group_name']
            if 'group_permissions' in body:
                group_permissions = body['group_permissions']

            if group_name is None or group_name == '':
                return custom_response(Code.INVALID_BODY, 'group_name not valid')

            if Group.objects.filter(name__iexact=group_name).exclude(pk=pk):
                return custom_response(Code.BAD_REQUEST, 'Group_name have been used by other group')

            group.name = group_name
            group.permissions.clear()
            group.permissions.set(group_permissions)
            group.save()

            return successful_response()
        except Exception as e:
            logging.error('Delete account_group_permission exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        """
            API delete account_group_permission
        """
        try:
            group = Group.objects.filter(pk=pk).first()
            if group is None:
                return custom_response(Code.GROUP_NOT_FOUND)

            group.delete()

            return successful_response()
        except Exception as e:
            logging.error('Delete account_group_permission exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

