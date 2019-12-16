import json
import logging

from django.db.models import Q
from django.conf import settings
from django.utils import formats
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view

from sale_portal.team import TeamType
from sale_portal.team.models import Team
from sale_portal.shop.models import Shop
from sale_portal.team.serializers import TeamSerializer
from sale_portal.staff.models import Staff, StaffTeamRole, StaffTeamLogType, StaffTeamRoleType
from sale_portal.staff.views import write_staff_team_log
from sale_portal.utils.field_formatter import format_string


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
            API create team \n
            Request body for this api : Không được bỏ trống \n
                {
                    "code": "team_code",
                    "name": "team name",
                    "type": 2, (type in {0,1,2} )
                    "description": "description",
                    "staffs": [
                        {
                            "id": 11732,
                            "role": "TEAM_STAFF"
                        },
                        {
                            "id": 351,
                            "role": "TEAM_MANAGEMENT"
                        }
                    ]
                }
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
                if team_lead_id in staff_ids:
                    staff_ids.remove(team_lead_id)
                write_staff_team_log(staff_ids, team, StaffTeamLogType.JOIN_TEAM,
                                     StaffTeamRoleType.TEAM_STAFF, 'Create new team: add staff')
                if team_lead_id is not None:
                    role_leader = StaffTeamRole.objects.filter(code='TEAM_MANAGEMENT').first()
                    Staff.objects.filter(pk=team_lead_id).update(
                        team=team,
                        role=role_leader
                    )
                    write_staff_team_log(team_lead_id, team, StaffTeamLogType.JOIN_TEAM,
                                         StaffTeamRoleType.TEAM_MANAGEMENT, 'Create new team: add management')

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
            API update Team \n
            Request body for this api : Không được bỏ trống \n
                {
                    "name": "team name",
                    "type": 2, (type in {0,1,2} )
                    "description": "description",
                    "staffs": [
                        {
                            "id": 11732,
                            "role": "TEAM_STAFF"
                        },
                        {
                            "id": 351,
                            "role": "TEAM_MANAGEMENT"
                        }
                    ]
                }
        """
        try:
            team = Team.objects.filter(pk=pk).first()
            if team is None:
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

            role_staff = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()
            role_leader = StaffTeamRole.objects.filter(code='TEAM_MANAGEMENT').first()
            staff_ids = []
            had_leader = False
            new_staff_ids = []
            new_leader_id = None
            update_to_staff_id = None
            update_to_leader_id = None
            for st in staffs:
                is_leader = False
                if not isinstance(st['id'], int):
                    return JsonResponse({
                        'status': 400,
                        'message': 'Invalid body (staff_id Invalid)'
                    }, status=400)

                staff_ids.append(st['id'])

                if st['role'] == 'TEAM_MANAGEMENT':
                    if had_leader:
                        return JsonResponse({
                            'status': 400,
                            'message': 'Team chỉ được phép có 1 leader'
                        }, status=400)
                    had_leader = True
                    is_leader = True
                elif st['role'] != 'TEAM_STAFF':
                    return JsonResponse({
                        'status': 400,
                        'message': 'Invalid body (staff_role Invalid)'
                    }, status=400)

                staff = Staff.objects.filter(pk=st['id']).first()
                if staff is None:
                    return JsonResponse({
                        'status': 400,
                        'message': 'staff_id ' + st['id'] + ' not found'
                    }, status=400)
                if staff.team is None:
                    if is_leader:
                        new_leader_id = st['id']
                    else:
                        new_staff_ids.append(st['id'])
                elif staff.team == team:
                    if staff.role is None or staff.role.code != st['role']:
                        if is_leader:
                            update_to_leader_id = st['id']
                        else:
                            update_to_staff_id = st['id']
                else:
                    return JsonResponse({
                        'status': 400,
                        'message': 'Nhân viên ' + staff.email + ' đang thuộc team khác'
                    }, status=400)

            staffs_remove = Staff.objects.filter(team=team).exclude(pk__in=staff_ids)
            if staffs_remove:
                remove_ids = []
                for id in staffs_remove.values('id'):
                    remove_ids.append(id['id'])

            with transaction.atomic():
                if staffs_remove:
                    Shop.objects.filter(staff__in=staffs_remove).update(
                        staff=None
                    )
                    staffs_remove.update(
                        team=None,
                        role=None
                    )
                    write_staff_team_log(remove_ids, team, StaffTeamLogType.OUT_TEAM,
                                         None, 'Update team: remove staff from team')
                if new_staff_ids:
                    Staff.objects.filter(pk__in=new_staff_ids).update(
                        team=team,
                        role=role_staff
                    )
                    write_staff_team_log(new_staff_ids, team, StaffTeamLogType.JOIN_TEAM,
                                         StaffTeamRoleType.TEAM_STAFF, 'Update team: add new staff')
                if new_leader_id is not None:
                    Staff.objects.filter(pk=new_leader_id).update(
                        team=team,
                        role=role_leader
                    )
                    write_staff_team_log(new_leader_id, team, StaffTeamLogType.JOIN_TEAM,
                                         StaffTeamRoleType.TEAM_MANAGEMENT, 'Update team: add new management')

                if update_to_staff_id is not None:
                    Staff.objects.filter(pk=update_to_staff_id).update(
                        role=role_staff
                    )
                    write_staff_team_log(update_to_staff_id, team, StaffTeamLogType.UPDATE_ROLE,
                                         StaffTeamRoleType.TEAM_STAFF, 'Update team: demote to staff')
                if update_to_leader_id is not None:
                    Staff.objects.filter(pk=update_to_leader_id).update(
                        role=role_leader
                    )
                    write_staff_team_log(update_to_leader_id, team, StaffTeamLogType.UPDATE_ROLE,
                                         StaffTeamRoleType.TEAM_MANAGEMENT, 'Update team: promote to management')

                team.name = name
                team.type = type
                team.description = description
                team.save()

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
            remove_ids = []
            for id in staffs.values('id'):
                remove_ids.append(id['id'])
            Shop.objects.filter(staff__in=staffs).update(
                staff=None
            )
            staffs.update(
                team=None,
                role=None
            )

            write_staff_team_log(remove_ids, team, StaffTeamLogType.OUT_TEAM,
                                 None, 'Delete team')
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
