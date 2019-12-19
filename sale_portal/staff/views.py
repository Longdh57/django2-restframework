import json
import logging

from datetime import datetime
from django.db.models import Q
from django.utils import formats
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins

from sale_portal.team.models import Team
from sale_portal.shop.models import Shop
from sale_portal.staff.serializers import StaffSerializer
from sale_portal.utils.field_formatter import format_string
from sale_portal.staff.models import Staff, StaffLogType, StaffTeamRole


class StaffViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
        API get list Staff \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - staff_code -- text
        - team_id -- number
        - full_name -- text
        - status -- number in {-1,1}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = StaffSerializer

    def get_queryset(self):

        queryset = Staff.objects.all()

        staff_code = self.request.query_params.get('staff_code', None)
        team_id = self.request.query_params.get('team_id', None)
        full_name = self.request.query_params.get('full_name', None)
        status = self.request.query_params.get('status', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if staff_code is not None and staff_code != '':
            staff_code = format_string(staff_code)
            queryset = queryset.filter(staff_code__icontains=staff_code)
        if team_id is not None and team_id != '':
            if team_id == '0':
                queryset = queryset.filter(team__isnull=True)
            else:
                queryset = queryset.filter(team_id=team_id)
        if full_name is not None and full_name != '':
            full_name = format_string(full_name)
            queryset = queryset.filter(Q(full_name__icontains=full_name) | Q(email__icontains=full_name))
        if status is not None and status != '':
            queryset = queryset.filter(status=(1 if status == '1' else -1))
        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

        return queryset

    def retrieve(self, request, pk):
        """
            API get detail Staff
        """
        team, role = None, None

        staff = Staff.objects.filter(pk=pk).first()
        if staff is None:
            return JsonResponse({
                'status': 404,
                'message': 'Staff not found'
            }, status=404)

        if staff.team is not None:
            team = {
                "name": staff.team.name,
                "code": staff.team.code,
                "created_date": formats.date_format(staff.team.created_date,
                                                    "SHORT_DATETIME_FORMAT") if staff.team.created_date else '',
            }

        if staff.role is not None:
            role = staff.role.code

        data = {
            'full_name': staff.full_name,
            'code': staff.staff_code,
            'email': staff.email,
            'mobile': staff.mobile,
            'status': staff.status,
            'team': team,
            'role': role,
            'created_date': formats.date_format(staff.created_date,
                                                "SHORT_DATETIME_FORMAT") if staff.created_date else '',
        }

        return JsonResponse({
            'status': 200,
            'data': data
        }, status=200)


@api_view(['GET'])
@login_required
def list_staffs(request):
    """
        API get list Staff to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - email -- text
        - team_id -- number
        - status -- number in {-1,1}
        - is_free -- true/false
    """

    queryset = Staff.objects.values('id', 'email', 'full_name')

    email = request.GET.get('email', None)
    team_id = request.GET.get('team_id', None)
    status = request.GET.get('status', None)
    is_free = request.GET.get('is_free', None)

    if email is not None and email != '':
        queryset = queryset.filter(Q(email__icontains=email) | Q(full_name__icontains=email))
    if status is not None and status != '':
        queryset = queryset.filter(status=status)
    if is_free is not None and is_free == 'true':
        queryset = queryset.filter(team=None)
    if team_id is not None and team_id != '':
        queryset = queryset.filter(team_id=team_id)

    queryset = queryset.order_by('email')[0:settings.PAGINATE_BY]

    data = [{'id': staff['id'], 'email': staff['full_name'] + ' - ' + staff['email']} for staff in queryset]

    return JsonResponse({
        'status': 200,
        'data': data
    }, status=200)


@api_view(['POST', 'PUT', 'DELETE'])
@login_required
def change_staff_team(request):
    """
        API update team for Staff (POST: create, PUT: update, DELETE: delete) \n
        Request body for this api : Không được bỏ trống \n
            {
                'staff_id' : 4,
                'team_id' : 6
            }
    """
    try:
        body = json.loads(request.body)

        staff_id = body.get('staff_id')
        team_id = body.get('team_id')

        if staff_id is None or staff_id == '' or team_id is None or team_id == '':
            return JsonResponse({
                'status': 400,
                'message': 'Invalid body'
            }, status=400)

        staff = Staff.objects.get(pk=staff_id)
        if staff is None:
            return JsonResponse({
                'status': 404,
                'message': 'Staff not found'
            }, status=404)

        team = Team.objects.get(pk=team_id)
        if team is None:
            return JsonResponse({
                'status': 404,
                'message': 'Team not found'
            }, status=404)

        role = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()
        # gan staff vao team moi
        if request.method == 'POST':
            if staff.team is not None:
                message = 'Staff đã thuộc team này từ trước'
                if staff.team.id != team.id:
                    message = 'Staff đang thuộc 1 Team khác'
                return JsonResponse({
                    'status': 400,
                    'message': message
                }, status=400)
            else:
                staff.team = team
                staff.role = role
                staff.save(
                    staff_id=staff.id,
                    team_id=team.id,
                    team_code=team.code,
                    role_id=role.id,
                    log_type=StaffLogType.JOIN_TEAM,
                    description='Change_staff_team: add new team',
                    user=request.user
                )
        # Thay doi team cho staff da duoc gan team
        if request.method == 'PUT':
            if staff.team is None or staff.team.id == team.id:
                message = 'Staff đã thuộc team này từ trước'
                if staff.team is None:
                    message = 'Staff đang không thuộc team nào, không thể chuyển Team'
                return JsonResponse({
                    'status': 400,
                    'message': message
                }, status=400)
            else:
                old_team = staff.team

                staff.team = team
                staff.role = role
                staff.save(
                    staff_id=staff.id,
                    old_team_id=old_team.id,
                    old_team_code=old_team.code,
                    team_id=team.id,
                    team_code=team.code,
                    role_id=role.id,
                    log_type=StaffLogType.OUT_TEAM,
                    description='Change_staff_team: out and join other team',
                    user=request.user
                )
                Shop.objects.filter(staff=staff).update(
                    staff=None
                )

        if request.method == 'DELETE':
            if staff.team is None or staff.team.id != team.id:
                message = 'Staff không thuộc team hiện tại'
                if staff.team is None:
                    message = 'Staff đang không thuộc team nào, không thể xóa Team'
                return JsonResponse({
                    'status': 400,
                    'message': message
                }, status=400)
            else:
                staff.team = None
                staff.role = None
                staff.save(
                    staff_id=staff.id,
                    team_id=team.id,
                    team_code=team.code,
                    role_id=None,
                    log_type=StaffLogType.OUT_TEAM,
                    description='Change_staff_team: out team',
                    user=request.user
                )
                Shop.objects.filter(staff=staff).update(
                    staff=None
                )

        return JsonResponse({
            'status': 200,
            'data': 'success'
        }, status=200)
    except Exception as e:
        logging.error('Update team for staff exception: %s', e)
        return JsonResponse({
            'status': 500,
            'data': 'Internal sever error'
        }, status=500)
