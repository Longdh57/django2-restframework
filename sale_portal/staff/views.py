import json
import logging
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins

from .models import Staff, StaffTeamRole
from .serializers import StaffSerializer
from ..utils.field_formatter import format_string
from ..team.models import Team
from ..shop.models import Shop


class StaffViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
        API get list Staff \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - staff_code -- text
        - full_name -- text
        - status -- number in {-1,1}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = StaffSerializer

    def get_queryset(self):

        queryset = Staff.objects.all()

        staff_code = self.request.query_params.get('staff_code', None)
        full_name = self.request.query_params.get('full_name', None)
        status = self.request.query_params.get('status', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if staff_code is not None and staff_code != '':
            staff_code = format_string(staff_code)
            queryset = queryset.filter(staff_code__icontains=staff_code)
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
        return JsonResponse({
            'status': 200,
            'data': "get detail method"
        }, status=200)


@api_view(['GET'])
@login_required
def list_staffs(request):
    """
        API get list Staff to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - email -- text
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
        Request body for this api : Không được bỏ trống
        - { \n
            'staff_id' : 4, \n
            'team_id' : 6 \n
            }
    """
    try:
        body = json.loads(request.body)
        staff_id = team_id = None
        if 'staff_id' in body:
            staff_id = body['staff_id']
        if 'team_id' in body:
            team_id = body['team_id']

        if staff_id is None or staff_id == '' or team_id is None or team_id == '':
            return JsonResponse({
                'status': 400,
                'message': 'Invalid body'
            }, status=400)

        staff = Staff.objects.filter(pk=staff_id).first()
        if staff is None:
            return JsonResponse({
                'status': 404,
                'message': 'Staff not found'
            }, status=404)
        team = Team.objects.filter(pk=team_id).first()
        if team is None:
            return JsonResponse({
                'status': 404,
                'message': 'Team not found'
            }, status=404)

        role = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()

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
                staff.save()

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
                staff.team = team
                staff.role = role
                staff.save()
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
                staff.save()
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
