import json
import logging
from django.contrib.auth.models import Group
from django.http import JsonResponse
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, mixins
from .serializers import UserSerializer, GroupSerializer
from ..staff.models import Staff
from ..staff import StaffTeamRoleType


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


class GroupViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
        API get list group_permission \n
    """
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]

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
                return JsonResponse({
                    'status': 400,
                    'message': 'Invalid body (group_name not valid)'
                }, status=400)

            group = Group.objects.filter(name__iexact=group_name)
            if group:
                return JsonResponse({
                    'status': 400,
                    'message': 'Group_name have been used'
                }, status=400)
            group = Group.objects.create(name=group_name)
            group.permissions.set(group_permissions)
            group.save()

            return JsonResponse({
                'status': 200,
                'data': group.id
            }, status=200)
        except Exception as e:
            logging.error('Create account_group_permission exception: %s', e)
            return JsonResponse({
                'status': 500,
                'data': 'Internal sever error'
            }, status=500)

    def retrieve(self, request, pk):
        """
            API get detail account_group_permission
        """
        group = Group.objects.filter(pk=pk).first()
        if group is None:
            return JsonResponse({
                'status': 404,
                'message': 'Groups not found'
            }, status=404)

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

        return JsonResponse({
            'status': 200,
            'data': data
        }, status=200)

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
                return JsonResponse({
                    'status': 404,
                    'message': 'Groups not found'
                }, status=404)

            body = json.loads(request.body)
            group_name = None
            group_permissions = []
            if 'group_name' in body:
                group_name = body['group_name']
            if 'group_permissions' in body:
                group_permissions = body['group_permissions']

            if group_name is None or group_name == '':
                return JsonResponse({
                    'status': 400,
                    'message': 'Invalid body (group_name not valid)'
                }, status=400)

            if Group.objects.filter(name__iexact=group_name).exclude(pk=pk):
                return JsonResponse({
                    'status': 400,
                    'message': 'Group_name have been used by other group'
                }, status=400)

            group.name = group_name
            group.permissions.clear()
            group.permissions.set(group_permissions)
            group.save()

            return JsonResponse({
                'status': 200,
                'data': 'success'
            }, status=200)
        except Exception as e:
            logging.error('Delete account_group_permission exception: %s', e)
            return JsonResponse({
                'status': 500,
                'data': 'Internal sever error'
            }, status=500)

    def destroy(self, request, pk):
        """
            API delete account_group_permission
        """
        try:
            group = Group.objects.filter(pk=pk).first()
            if group is None:
                return JsonResponse({
                    'status': 404,
                    'message': 'Groups not found'
                }, status=404)

            group.delete()

            return JsonResponse({
                'status': 200,
                'data': 'success'
            }, status=200)
        except Exception as e:
            logging.error('Delete account_group_permission exception: %s', e)
            return JsonResponse({
                'status': 500,
                'data': 'Internal sever error'
            }, status=500)

