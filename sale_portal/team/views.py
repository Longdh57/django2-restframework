import json
import logging

from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.utils import formats
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view

from sale_portal.area.models import Area
from sale_portal.staff import StaffTeamRoleType
from sale_portal.user import ROLE_SALE, ROLE_SALE_LEADER
from sale_portal.user.views import update_role_for_staff
from sale_portal.utils.permission import get_user_permission_classes
from sale_portal.team import TeamType
from sale_portal.team.models import Team
from sale_portal.staff_care.models import StaffCare, StaffCareLog
from sale_portal.team.serializers import TeamSerializer
from sale_portal.utils.field_formatter import format_string
from sale_portal.staff.models import Staff, StaffLog, StaffLogType
from sale_portal.utils.queryset import get_teams_viewable_queryset

from ..common.standard_response import successful_response, custom_response, Code


class TeamViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list Team \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
    """
    serializer_class = TeamSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('team.team_list_data', self.request)
        if self.action == 'retrieve':
            permission_classes = get_user_permission_classes('team.team_detail', self.request)
        if self.action == 'create':
            permission_classes = get_user_permission_classes('team.team_create', self.request)
        if self.action == 'update':
            permission_classes = get_user_permission_classes('team.team_edit', self.request)
        if self.action == 'destroy':
            permission_classes = get_user_permission_classes('team.team_delete', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):

        queryset = Team.objects.all()

        if self.request.user.is_superuser is False:
            teams = get_teams_viewable_queryset(self.request.user)
            queryset = queryset.filter(pk__in=teams)

        name = self.request.query_params.get('name', None)
        code = self.request.query_params.get('code', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if name is not None and name != '':
            name = format_string(name)
            queryset = queryset.filter(name__icontains=name)
        if code is not None and code != '':
            code = format_string(code)
            queryset = queryset.filter(code__icontains=code)
        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

        return queryset

    def create(self, request):
        """
            API create team \n
            Request body for this api : Không được bỏ trống \n
                {
                    "code": "DN1",
                    "name": "Team Da Nang",
                    "type": 2, (type in {0,1,2} )
                    "description": "description",
                    "area_id": 1,
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

            name = body.get('name')
            code = body.get('code')
            type = body.get('type')
            area_id = body.get('area_id')
            description = body.get('description')
            staffs = body.get('staffs')

            if staffs is not None and staffs != '' and not isinstance(staffs, list):
                return custom_response(Code.INVALID_BODY, 'staffs Invalid')

            if type is not None and type != '':
                if not (isinstance(type, int) and 0 <= type <= 2):
                    return custom_response(Code.INVALID_BODY, 'type Invalid')
            else:
                type = 0

            if name is None or name == '' or code is None or code == '':
                return custom_response(Code.INVALID_BODY, 'name or code Invalid')

            name = format_string(name)
            code = format_string(code)

            if Team.objects.filter(Q(name__iexact=name) | Q(code__iexact=code)):
                return custom_response(Code.BAD_REQUEST, 'name or code be used by other Team')

            if not isinstance(area_id, int):
                return custom_response(Code.INVALID_BODY, 'area_id not valid')
            area = Area.objects.filter(pk=area_id).first()
            if area is None:
                return custom_response(Code.AREA_NOT_FOUND)

            # validate staff_list
            staff_ids = []
            team_lead_id = None
            had_leader = False
            if staffs is not None and staffs != '':
                for staff in staffs:
                    if not isinstance(staff['id'], int):
                        return custom_response(Code.INVALID_BODY, 'staff_id Invalid')
                    staff_ids.append(staff['id'])
                    if staff['role'] == StaffTeamRoleType.CHOICES[StaffTeamRoleType.TEAM_MANAGEMENT][1]:
                        if had_leader:
                            return custom_response(Code.INVALID_BODY, 'Team chỉ được phép có 1 leader')
                        had_leader = True
                        team_lead_id = staff['id']
                    elif staff['role'] != StaffTeamRoleType.CHOICES[StaffTeamRoleType.TEAM_STAFF][1]:
                        return custom_response(Code.INVALID_BODY, 'staff_role Invalid')

                if staff_ids:
                    if len(staff_ids) != Staff.objects.filter(pk__in=staff_ids).count():
                        return custom_response(Code.STAFF_NOT_FOUND)

                staff_have_teams = Staff.objects.filter(pk__in=staff_ids, team__isnull=False)

                if staff_have_teams:
                    staff_emails = ''
                    for staff in staff_have_teams:
                        staff_emails += staff.email + ', '
                    staff_emails = staff_emails[:-2]
                    return custom_response(Code.BAD_REQUEST, 'Các nhân viên: ' + staff_emails + ' đang thuộc team khác')

            team = Team(
                code=code.upper(),
                name=name,
                type=type,
                area=area,
                description=description,
                created_by=request.user,
                updated_by=request.user
            )
            team.save(user=request.user)

            if staffs is not None and staffs != '':
                role_staff = StaffTeamRoleType.TEAM_STAFF
                Staff.objects.filter(pk__in=staff_ids).exclude(pk=team_lead_id).update(
                    team=team,
                    role=role_staff
                )
                if team_lead_id in staff_ids:
                    staff_ids.remove(team_lead_id)
                self.create_staff_log(
                    staff_ids=staff_ids,
                    team=team,
                    type=StaffLogType.JOIN_TEAM,
                    role=role_staff,
                    description='Create new team: add staff'
                )
                update_role_for_staff(staff_ids, ROLE_SALE)

                if team_lead_id is not None:
                    role_leader = StaffTeamRoleType.TEAM_MANAGEMENT
                    staff = Staff.objects.get(pk=team_lead_id)
                    staff.team = team
                    staff.role = role_leader
                    staff.save(
                        staff_id=staff.id,
                        team_id=team.id,
                        team_code=team.code,
                        role=role_leader,
                        log_type=StaffLogType.JOIN_TEAM,
                        description='Create new team: add management',
                        user=request.user
                    )
                    update_role_for_staff([team_lead_id], ROLE_SALE_LEADER)

            return successful_response(team.id)

        except Exception as e:
            logging.error('Create team exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        """
            API get detail Team
        """
        if request.user.is_superuser is False:
            teams = get_teams_viewable_queryset(request.user)
            team = Team.objects.filter(pk=pk, pk__in=teams).first()
        else:
            team = Team.objects.filter(pk=pk).first()

        if team is None:
            return custom_response(Code.TEAM_NOT_FOUND)

        members = []
        staffs = team.staff_set.all()

        area = {
            'id': team.area.id if team.area else '',
            'name': team.area.name if team.area else ''
        }

        for staff in staffs:
            member = {
                'id': staff.id,
                'staff_code': staff.staff_code,
                'full_name': staff.full_name,
                'email': staff.email,
                'status': staff.status,
                # check choice
                'role': staff.get_role_name()
            }
            members.append(member)

        data = {
            'name': team.name,
            'code': team.code,
            'type': TeamType.CHOICES[team.type][1],
            'description': team.description,
            'area': team.area.name if team.area else '',
            'members': members,
            'area': area,
            'created_date': formats.date_format(team.created_date,
                                                "SHORT_DATETIME_FORMAT") if team.created_date else '',
        }

        return successful_response(data)

    def update(self, request, pk):
        """
            API update Team \n
            Request body for this api : Không được bỏ trống \n
                {
                    "name": "team name",
                    "type": 2, (type in {0,1,2} )
                    "description": "description",
                    "area_id": 1,
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
                return custom_response(Code.TEAM_NOT_FOUND)
            body = json.loads(request.body)

            name = body.get('name')
            type = body.get('type')
            description = body.get('description')
            staffs = body.get('staffs')
            area_id = body.get('area_id')

            if staffs is not None and staffs != '':
                if not isinstance(staffs, list):
                    return custom_response(Code.INVALID_BODY, 'staffs Invalid')
            else:
                staffs = []

            if name is None or name == '':
                return custom_response(Code.INVALID_BODY, 'name Invalid')

            if type is None and type == '' or not (isinstance(type, int) and 0 <= type <= 2):
                return custom_response(Code.INVALID_BODY, 'type Invalid')

            name = format_string(name)

            if Team.objects.filter(name__iexact=name).exclude(pk=pk):
                return custom_response(Code.BAD_REQUEST, 'name being used by other Team')

            area = None
            if area_id is not None and area_id != '':
                if not isinstance(area_id, int):
                    return custom_response(Code.INVALID_BODY, 'area_id not valid')
                area = Area.objects.filter(pk=area_id).first()
                if area is None:
                    return custom_response(Code.AREA_NOT_FOUND)

            role_staff = StaffTeamRoleType.TEAM_STAFF
            role_leader = StaffTeamRoleType.TEAM_MANAGEMENT

            staff_ids = []
            had_leader = False
            new_staff_ids = []
            new_leader_id = None
            update_to_staff_id = None
            update_to_leader_id = None

            # Validate staff lists
            for st in staffs:
                is_leader = False
                if not isinstance(st['id'], int):
                    return custom_response(Code.INVALID_BODY, 'staff_id Invalid')

                staff_ids.append(st['id'])

                if st['role'] == StaffTeamRoleType.CHOICES[StaffTeamRoleType.TEAM_MANAGEMENT][1]:
                    if had_leader:
                        return custom_response(Code.INVALID_BODY, 'Team chỉ được phép có 1 leader')
                    had_leader = True
                    is_leader = True
                elif st['role'] != StaffTeamRoleType.CHOICES[StaffTeamRoleType.TEAM_STAFF][1]:
                    return custom_response(Code.INVALID_BODY, 'staff_role Invalid')

                staff = Staff.objects.filter(pk=st['id']).first()
                if staff is None:
                    return custom_response(Code.STAFF_NOT_FOUND, 'staff_id ' + str(st['id']) + ' not found')
                if staff.team is None:
                    if is_leader:
                        new_leader_id = st['id']
                    else:
                        new_staff_ids.append(st['id'])
                elif staff.team == team:
                    if StaffTeamRoleType.CHOICES[staff.role][1] != st['role']:
                        if is_leader:
                            update_to_leader_id = st['id']
                        else:
                            update_to_staff_id = st['id']
                else:
                    return custom_response(Code.BAD_REQUEST, 'Nhân viên ' + staff.email + ' đang thuộc team khác')

            staffs_remove = Staff.objects.filter(team=team).exclude(pk__in=staff_ids)
            remove_ids = []
            if staffs_remove:
                for id in staffs_remove.values('id'):
                    remove_ids.append(id['id'])

            with transaction.atomic():
                if staffs_remove:
                    StaffCare.objects.filter(staff__in=staffs_remove).delete()
                    StaffCareLog.objects.filter(staff__in=staffs_remove, is_caring=True).update(
                        is_caring=False,
                        updated_by=request.user,
                        updated_date=datetime.now(),
                    )

                    staffs_remove.update(
                        team=None,
                        role=StaffTeamRoleType.FREELANCE_STAFF
                    )
                    self.create_staff_log(
                        staff_ids=remove_ids,
                        team=team,
                        type=StaffLogType.OUT_TEAM,
                        role=StaffTeamRoleType.FREELANCE_STAFF,
                        description='Update team: remove staff from team'
                    )
                    update_role_for_staff(remove_ids, ROLE_SALE)

                if new_staff_ids:
                    Staff.objects.filter(pk__in=new_staff_ids).update(
                        team=team,
                        role=role_staff
                    )
                    self.create_staff_log(
                        staff_ids=new_staff_ids,
                        team=team,
                        type=StaffLogType.JOIN_TEAM,
                        role=role_staff,
                        description='Update team: add new staff'
                    )
                    update_role_for_staff(new_staff_ids, ROLE_SALE)

                if new_leader_id is not None:
                    staff = Staff.objects.get(pk=new_leader_id)
                    staff.team = team
                    staff.role = role_leader
                    staff.save(
                        staff_id=new_leader_id,
                        team_id=team.id,
                        team_code=team.code,
                        role=role_leader,
                        log_type=StaffLogType.JOIN_TEAM,
                        description='Update team: add new management',
                        user=request.user
                    )
                    update_role_for_staff([new_leader_id], ROLE_SALE_LEADER)

                if update_to_staff_id is not None:
                    staff = Staff.objects.get(pk=update_to_staff_id)
                    staff.role = role_staff
                    staff.save(
                        staff_id=update_to_staff_id,
                        team_id=team.id,
                        team_code=team.code,
                        role=role_staff,
                        log_type=StaffLogType.UPDATE_ROLE,
                        description='Update team: demote to staff',
                        user=request.user
                    )
                    update_role_for_staff([update_to_staff_id], ROLE_SALE)

                if update_to_leader_id is not None:
                    staff = Staff.objects.get(pk=update_to_leader_id)
                    staff.role = role_leader
                    staff.save(
                        staff_id=update_to_leader_id,
                        team_id=team.id,
                        team_code=team.code,
                        role=role_leader,
                        log_type=StaffLogType.UPDATE_ROLE,
                        description='Update team: promote to management',
                        user=request.user
                    )
                    update_role_for_staff([update_to_leader_id], ROLE_SALE_LEADER)

                team.name = name
                team.type = type
                team.description = description
                team.updated_by = request.user
                if area is not None:
                    team.area = area
                team.save(user=request.user, action="update")

            return successful_response()
        except Exception as e:
            logging.error('Update team exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        """
            API delete Team
        """
        try:
            team = Team.objects.filter(pk=pk).first()
            if team is None:
                return custom_response(Code.TEAM_NOT_FOUND)
            staffs = team.staff_set.all()
            remove_ids = []
            for id in staffs.values('id'):
                remove_ids.append(id['id'])
            update_role_for_staff(remove_ids, ROLE_SALE)

            StaffCare.objects.filter(staff__in=staffs).delete()
            StaffCareLog.objects.filter(staff__in=staffs, is_caring=True).update(
                is_caring=False,
                updated_by=request.user,
                updated_date=datetime.now(),
            )

            staffs.update(
                team=None,
                role=StaffTeamRoleType.FREELANCE_STAFF
            )

            self.create_staff_log(
                staff_ids=remove_ids,
                team=team,
                type=StaffLogType.OUT_TEAM,
                role=StaffTeamRoleType.FREELANCE_STAFF,
                description='Delete team'
            )

            team.delete(user=request.user)

            return successful_response()

        except Exception as e:
            logging.error('Delete team exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def create_staff_log(self, staff_ids, team, type, role, description, user=None):
        try:
            staff_logs = []

            for staff_id in staff_ids:
                staff_logs.append(StaffLog(
                    staff_id=staff_id,
                    team_id=team.id,
                    team_code=team.code,
                    type=type,
                    role=role,
                    description=description,
                    created_by=user or None)
                )
            StaffLog.objects.bulk_create(staff_logs)
        except Exception as e:
            logging.error("Create team - Staff log: {}".format(e))


@api_view(['GET'])
@login_required
@permission_required('team.team_list_data', raise_exception=True)
def list_teams(request):
    """
        API get list Team to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
    """

    queryset = Team.objects.values('id', 'code', 'name')

    if request.user.is_superuser is False:
        teams = get_teams_viewable_queryset(request.user)
        queryset = queryset.filter(pk__in=teams)

    code = request.GET.get('code', None)

    if code is not None and code != '':
        queryset = queryset.filter(Q(name__icontains=code) | Q(code__icontains=code))

    queryset = queryset.order_by('name')[0:settings.PAGINATE_BY]

    data = [{'id': team['id'], 'name': team['name'] + ' - ' + team['code']} for team in queryset]

    return successful_response(data)
