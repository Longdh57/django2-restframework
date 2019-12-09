import json
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.utils import formats
from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins

from sale_portal.team import TeamType
from .models import Team
from .serializers import TeamSerializer
from ..utils.field_formatter import format_string
from ..shop.models import Shop
from ..staff.models import Staff, StaffTeamRole


class TeamViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
        API get list Team \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
    """
    serializer_class = TeamSerializer

    def get_queryset(self):

        queryset = Team.objects.all()

        name = self.request.query_params.get('name', None)

        if name is not None and name != '':
            name = format_string(name)
            queryset = queryset.filter(Q(name__icontains=name) | Q(code__icontains=name))

        return queryset

    def create(self, request):
        """
            API create team
        """
        try:
            body = json.loads(request.body)
            name = code = description = type = staffs = None
            if 'name' in body:
                name = body['name']
            if 'code' in body:
                code = body['code']
            if 'type' in body:
                type = body['type']
            if 'description' in body:
                description = body['description']
            if 'staffs' in body:
                staffs = body['staffs']

            if staffs is not None and staffs != '' and not isinstance(staffs, list):
                return JsonResponse({
                    'status': 400,
                    'message': 'Invalid body (staffs Invalid)'
                }, status=400)

            if type is not None and type != '':
                if not (isinstance(type, int) and 0 <= type <= 2):
                    return JsonResponse({
                        'status': 400,
                        'message': 'Invalid body (type Invalid)'
                    }, status=400)
            else:
                type = 0

            if name is None or name == '' or code is None or code == '':
                return JsonResponse({
                    'status': 400,
                    'message': 'Invalid body (name or code Invalid)'
                }, status=400)

            name = format_string(name)
            code = format_string(code)

            if Team.objects.filter(Q(name__iexact=name) | Q(code__iexact=code)):
                return JsonResponse({
                    'status': 400,
                    'message': 'name or code be used by other Team'
                }, status=400)

            if staffs is not None and staffs != '':
                staff_ids = []
                team_lead_id = None
                had_leader = False
                for staff in staffs:
                    if not isinstance(staff['id'], int):
                        return JsonResponse({
                            'status': 400,
                            'message': 'Invalid body (staff_id Invalid)'
                        }, status=400)
                    staff_ids.append(staff['id'])
                    if staff['role'] == 'TEAM_MANAGEMENT':
                        if had_leader:
                            return JsonResponse({
                                'status': 400,
                                'message': 'Team chỉ được phép có 1 leader'
                            }, status=400)
                        had_leader = True
                        team_lead_id = staff['id']
                    elif staff['role'] != 'TEAM_STAFF':
                        return JsonResponse({
                            'status': 400,
                            'message': 'Invalid body (staff_role Invalid)'
                        }, status=400)

                if staff_ids:
                    if len(staff_ids) != Staff.objects.filter(pk__in=staff_ids).count():
                        return JsonResponse({
                            'status': 400,
                            'message': 'Invalid body (Staff not found)'
                        }, status=400)

                staff_have_teams = Staff.objects.filter(pk__in=staff_ids, team__isnull=False)

                if staff_have_teams:
                    staff_emails = ''
                    for staff in staff_have_teams:
                        staff_emails += staff.email + ', '
                    staff_emails = staff_emails[:-2]
                    return JsonResponse({
                        'status': 400,
                        'message': 'Các nhân viên: ' + staff_emails + ' đang thuộc team khác'
                    }, status=400)

            team = Team(
                code=code.upper(),
                name=name,
                type=type,
                description=description
            )
            team.save()

            if staffs is not None and staffs != '':
                role_staff = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()
                Staff.objects.filter(pk__in=staff_ids).exclude(pk=team_lead_id).update(
                    team=team,
                    role=role_staff
                )

                if team_lead_id is not None:
                    role_leader = StaffTeamRole.objects.filter(code='TEAM_MANAGEMENT').first()
                    Staff.objects.filter(pk=team_lead_id).update(
                        team=team,
                        role=role_leader
                    )

            return JsonResponse({
                'status': 200,
                'data': team.id
            }, status=201)
        except Exception as e:
            logging.error('Create team exception: %s', e)
            return JsonResponse({
                'status': 500,
                'data': 'Internal sever error'
            }, status=500)

    def retrieve(self, request, pk):
        """
            API get detail Team
        """
        team = Team.objects.filter(pk=pk).first()
        if team is None:
            return JsonResponse({
                'status': 404,
                'message': 'Team not found'
            }, status=404)

        members = []
        staffs = team.staff_set.all()

        for staff in staffs:
            member = {
                'id': staff.id,
                'staff_code': staff.staff_code,
                'full_name': staff.full_name,
                'email': staff.email,
                'status': staff.status,
                'role': staff.role.code if staff.role else ''
            }
            members.append(member)

        data = {
            'name': team.name,
            'code': team.code,
            'type': TeamType.CHOICES[team.type][1],
            'description': team.description,
            'members': members,
            'created_date': formats.date_format(team.created_date,
                                                "SHORT_DATETIME_FORMAT") if team.created_date else '',
        }

        return JsonResponse({
            'status': 200,
            'data': data
        }, status=200)

    def update(self, request, pk):
        """
            API update Team
        """
        try:
            team = Team.objects.filter(pk=pk)
            if not team:
                return JsonResponse({
                    'status': 404,
                    'message': 'Team not found'
                }, status=404)
            body = json.loads(request.body)
            name = description = type = staffs = None
            if 'name' in body:
                name = body['name']
            if 'type' in body:
                type = body['type']
            if 'description' in body:
                description = body['description']
            if 'staffs' in body:
                staffs = body['staffs']

            if staffs is not None and staffs != '':
                if not isinstance(staffs, list):
                    return JsonResponse({
                        'status': 400,
                        'message': 'Invalid body (staffs Invalid)'
                    }, status=400)
            else:
                staffs = []

            if name is None or name == '':
                return JsonResponse({
                    'status': 400,
                    'message': 'Invalid body (name Invalid)'
                }, status=400)

            if type is None and type == '' or not (isinstance(type, int) and 0 <= type <= 2):
                return JsonResponse({
                    'status': 400,
                    'message': 'Invalid body (type Invalid)'
                }, status=400)

            name = format_string(name)

            if Team.objects.filter(name__iexact=name).exclude(pk=pk):
                return JsonResponse({
                    'status': 400,
                    'message': 'name being used by other Team'
                }, status=400)

            staff_ids = []
            had_leader = False

            role_staff = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()
            role_leader = StaffTeamRole.objects.filter(code='TEAM_MANAGEMENT').first()

            with transaction.atomic():
                for st in staffs:
                    is_leader = False
                    if not isinstance(st['id'], int):
                        raise Exception('Invalid body (staff_id Invalid)')

                    staff_ids.append(st['id'])

                    if st['role'] == 'TEAM_MANAGEMENT':
                        if had_leader:
                            raise Exception('Team chỉ được phép có 1 leader')
                        had_leader = True
                        is_leader = True
                    elif st['role'] != 'TEAM_STAFF':
                        raise Exception('Invalid body (staff_role Invalid)')

                    staff = Staff.objects.filter(pk=st['id']).first()
                    if staff is None:
                        raise Exception('staff_id ' + st['id'] + ' not found')
                    if staff.team is None:
                        staff.team = team
                        staff.role = role_leader if is_leader else role_staff
                        staff.save()
                    elif staff.team == team:
                        if staff.role is None or staff.role.code != st['role']:
                            staff.role = role_leader if is_leader else role_staff
                            staff.save()
                    else:
                        raise Exception('Nhân viên ' + staff.email + ' đang thuộc team khác')

                staffs_remove = Staff.objects.filter(team=team).exclude(pk__in=staff_ids)
                if staffs_remove:
                    Shop.objects.filter(staff__in=staffs_remove).update(
                        staff=None
                    )
                    staffs_remove.update(
                        team=None,
                        role=None
                    )

                team.update(
                    name=name,
                    type=type,
                    description=description
                )

            return JsonResponse({
                'status': 200,
                'data': 'success'
            }, status=200)
        except Exception as e:
            logging.error('Update team exception: %s', e)
            return JsonResponse({
                'status': 500,
                'data': 'Internal sever error'
            }, status=500)

    def destroy(self, request, pk):
        """
            API delete Team
        """
        try:
            team = Team.objects.filter(pk=pk).first()
            if team is None:
                return JsonResponse({
                    'status': 404,
                    'message': 'Team not found'
                }, status=404)
            staffs = team.staff_set.all()
            Shop.objects.filter(staff__in=staffs).update(
                staff=None
            )
            staffs.update(
                team=None,
                role=None
            )
            team.delete()
            return JsonResponse({
                'status': 200,
                'data': 'success'
            }, status=200)
        except Exception as e:
            logging.error('Delete team exception: %s', e)
            return JsonResponse({
                'status': 500,
                'data': 'Internal sever error'
            }, status=500)


@api_view(['GET'])
@login_required
def list_teams(request):
    """
        API get list Team to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
    """

    queryset = Team.objects.values('id', 'code', 'name')

    code = request.GET.get('code', None)

    if code is not None and code != '':
        queryset = queryset.filter(Q(name__icontains=code) | Q(code__icontains=code))

    queryset = queryset.order_by('name')[0:settings.PAGINATE_BY]

    data = [{'id': team['id'], 'name': team['name'] + ' - ' + team['code']} for team in queryset]

    return JsonResponse({
        'status': 200,
        'data': data
    }, status=200)
