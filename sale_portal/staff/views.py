import json
import logging

from datetime import datetime
from django.db.models import Q
from django.utils import formats
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required

from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins

from sale_portal.staff import StaffTeamRoleType
from sale_portal.user import ROLE_SALE
from sale_portal.user.views import update_role_for_staff
from sale_portal.utils.permission import get_user_permission_classes
from sale_portal.staff_care.models import StaffCare, StaffCareLog
from sale_portal.team.models import Team
from sale_portal.staff.serializers import StaffSerializer
from sale_portal.utils.field_formatter import format_string
from sale_portal.staff.models import Staff, StaffLogType
from sale_portal.utils.queryset import get_staffs_viewable_queryset

from ..common.standard_response import Code, successful_response, custom_response


class StaffViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
        API get list Staff \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - staff_code -- text
        - team_id -- number
        - role -- number in {1,2}
        - status -- number in {-1,1}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = StaffSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('staff.staff_list_data', self.request)
        if self.action == 'retrieve':
            permission_classes = get_user_permission_classes('staff.staff_detail', self.request)
        if self.action == 'update':
            permission_classes = get_user_permission_classes('staff.staff_edit', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):

        queryset = Staff.objects.all()

        if self.request.user.is_superuser is False:
            staffs = get_staffs_viewable_queryset(self.request.user)
            queryset = queryset.filter(pk__in=staffs)

        staff_code = self.request.query_params.get('staff_code', None)
        team_id = self.request.query_params.get('team_id', None)
        role = self.request.query_params.get('role', None)
        status = self.request.query_params.get('status', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if staff_code is not None and staff_code != '':
            staff_code = format_string(staff_code)
            queryset = queryset.filter(Q(staff_code__icontains=staff_code) | Q(full_name__icontains=staff_code) | Q(
                email__icontains=staff_code))
        if team_id is not None and team_id != '':
            if team_id == '0':
                queryset = queryset.filter(team__isnull=True)
            else:
                queryset = queryset.filter(team_id=team_id)
        if role is not None and role != '':
            if role.isdigit():
                if int(role) == 2:
                    queryset = queryset.filter(Q(role=int(role)) | Q(role=0))
                else:
                    queryset = queryset.filter(role=int(role))
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

        if request.user.is_superuser is False:
            staffs = get_staffs_viewable_queryset(request.user)
            staff = Staff.objects.filter(pk=pk, pk__in=staffs).first()
        else:
            staff = Staff.objects.filter(pk=pk).first()

        if staff is None:
            return custom_response(Code.STAFF_NOT_FOUND)

        team = {
            "name": staff.team.name,
            "code": staff.team.code,
            "created_date": formats.date_format(staff.team.created_date,
                                                "SHORT_DATETIME_FORMAT") if staff.team.created_date else '',
        } if staff.team is not None else None

        data = {
            'full_name': staff.full_name,
            'code': staff.staff_code,
            'email': staff.email,
            'mobile': staff.mobile,
            'status': staff.status,
            'team': team,
            'role': staff.get_role_name(),
            'created_date': formats.date_format(staff.created_date,
                                                "SHORT_DATETIME_FORMAT") if staff.created_date else '',
        }

        return successful_response(data)


@api_view(['GET'])
@login_required
@permission_required('staff.staff_list_data', raise_exception=True)
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

    if request.user.is_superuser is False:
        staffs = get_staffs_viewable_queryset(request.user)
        queryset = queryset.filter(pk__in=staffs)

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

    return successful_response(data)


@api_view(['POST', 'PUT', 'DELETE'])
@login_required
@permission_required('staff.staff_edit', raise_exception=True)
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
            return custom_response(Code.INVALID_BODY)

        staff = Staff.objects.filter(pk=staff_id).first()
        if staff is None:
            return custom_response(Code.STAFF_NOT_FOUND)
        team = Team.objects.filter(pk=team_id).first()
        if team is None:
            return custom_response(Code.TEAM_NOT_FOUND)

        role = StaffTeamRoleType.TEAM_STAFF

        # gan staff vao team moi
        if request.method == 'POST':
            if staff.team is not None:
                message = 'Staff đã thuộc team này từ trước'
                if staff.team.id != team.id:
                    message = 'Staff đang thuộc 1 Team khác'
                return custom_response(Code.BAD_REQUEST, message)
            else:
                staff.team = team
                staff.role = role
                staff.save(
                    staff_id=staff.id,
                    team_id=team.id,
                    team_code=team.code,
                    role=role,
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
                return custom_response(Code.BAD_REQUEST, message)
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
                    role=role,
                    log_type=StaffLogType.OUT_TEAM,
                    description='Change_staff_team: out and join other team',
                    user=request.user
                )
                StaffCare.objects.filter(staff=staff).delete()
                StaffCareLog.objects.filter(staff=staff, is_caring=True).update(
                    is_caring=False,
                    updated_by=request.user,
                    updated_date=datetime.now(),
                )

        if request.method == 'DELETE':
            if staff.team is None or staff.team.id != team.id:
                message = 'Staff không thuộc team hiện tại'
                if staff.team is None:
                    message = 'Staff đang không thuộc team nào, không thể xóa Team'
                return custom_response(Code.BAD_REQUEST, message)
            else:
                staff.team = None
                staff.role = StaffTeamRoleType.FREELANCE_STAFF
                staff.save(
                    staff_id=staff.id,
                    team_id=team.id,
                    team_code=team.code,
                    role=StaffTeamRoleType.FREELANCE_STAFF,
                    log_type=StaffLogType.OUT_TEAM,
                    description='Change_staff_team: out team',
                    user=request.user
                )
                StaffCare.objects.filter(staff=staff).delete()
                StaffCareLog.objects.filter(staff=staff, is_caring=True).update(
                    is_caring=False,
                    updated_by=request.user,
                    updated_date=datetime.now(),
                )

        update_role_for_staff([staff_id], ROLE_SALE)

        return successful_response()
    except Exception as e:
        logging.error('Update team for staff exception: %s', e)
        return custom_response(Code.INTERNAL_SERVER_ERROR)
