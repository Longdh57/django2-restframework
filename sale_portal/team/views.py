import json
import logging

from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.utils import formats
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required

from rest_framework import permissions
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view

from sale_portal.team import TeamType
from sale_portal.team.models import Team
from sale_portal.staff_care.models import StaffCare
from sale_portal.team.serializers import TeamSerializer
from sale_portal.utils.field_formatter import format_string
from sale_portal.staff.models import Staff, StaffLog, StaffLogType, StaffTeamRole

from ..common.standard_response import successful_response, custom_response, Code


class PermissionReadData(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            list_permission = ['team.team_list_data', 'team.team_detail']
            return any(request.user.has_perm(permission) for permission in list_permission)
        return False


class PermissionWriteData(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            list_permission = ['team.team_create', 'team.team_edit', 'team.team_delete']
            return any(request.user.has_perm(permission) for permission in list_permission)
        return False


class TeamViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list Team \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
    """
    serializer_class = TeamSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [PermissionReadData]
        else:
            permission_classes = [PermissionWriteData]
        return [permission() for permission in permission_classes]

    def get_queryset(self):

        queryset = Team.objects.all()

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
                    "area_id": 1
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

            # if not isinstance(area_id, int):
            #     return custom_response(Code.INVALID_BODY, 'area_id not valid')
            # area = Area.objects.filter(pk=area_id).first()
            # if area is None:
            #     return custom_response(Code.AREA_NOT_FOUND)

            # validate staff_list
            staff_ids = []
            team_lead_id = None
            had_leader = False
            if staffs is not None and staffs != '':
                for staff in staffs:
                    if not isinstance(staff['id'], int):
                        return custom_response(Code.INVALID_BODY, 'staff_id Invalid')
                    staff_ids.append(staff['id'])
                    if staff['role'] == 'TEAM_MANAGEMENT':
                        if had_leader:
                            return custom_response(Code.INVALID_BODY, 'Team chỉ được phép có 1 leader')
                        had_leader = True
                        team_lead_id = staff['id']
                    elif staff['role'] != 'TEAM_STAFF':
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
                # area=area,
                description=description,
                created_by=request.user,
                updated_by=request.user
            )
            team.save(user=request.user)

            if staffs is not None and staffs != '':
                role_staff = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()
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
                    role_id=role_staff.id,
                    description='Create new team: add staff'
                )

                if team_lead_id is not None:
                    role_leader = StaffTeamRole.objects.filter(code='TEAM_MANAGEMENT').first()
                    staff = Staff.objects.get(pk=team_lead_id)
                    staff.team = team
                    staff.role = role_leader
                    staff.save(
                        staff_id=staff.id,
                        team_id=team.id,
                        team_code=team.code,
                        role_id=role_leader.id,
                        log_type=StaffLogType.JOIN_TEAM,
                        description='Create new team: add management',
                        user=request.user
                    )

            return successful_response(team.id)

        except Exception as e:
            logging.error('Create team exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        """
            API get detail Team
        """
        team = Team.objects.filter(pk=pk).first()
        if team is None:
            return custom_response(Code.TEAM_NOT_FOUND)

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
            'area': team.area.name if team.area else '',
            'members': members,
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

            role_staff = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()
            role_leader = StaffTeamRole.objects.filter(code='TEAM_MANAGEMENT').first()

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

                if st['role'] == 'TEAM_MANAGEMENT':
                    if had_leader:
                        return custom_response(Code.INVALID_BODY, 'Team chỉ được phép có 1 leader')
                    had_leader = True
                    is_leader = True
                elif st['role'] != 'TEAM_STAFF':
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
                    if staff.role is None or staff.role.code != st['role']:
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

                    staffs_remove.update(
                        team=None,
                        role=None
                    )
                    self.create_staff_log(
                        staff_ids=remove_ids,
                        team=team,
                        type=StaffLogType.OUT_TEAM,
                        role_id=None,
                        description='Update team: remove staff from team'
                    )

                if new_staff_ids:
                    Staff.objects.filter(pk__in=new_staff_ids).update(
                        team=team,
                        role=role_staff
                    )
                    self.create_staff_log(
                        staff_ids=new_staff_ids,
                        team=team,
                        type=StaffLogType.JOIN_TEAM,
                        role_id=role_staff.id,
                        description='Update team: add new staff'
                    )

                if new_leader_id is not None:
                    staff = Staff.objects.get(pk=new_leader_id)
                    staff.team = team
                    staff.role = role_leader
                    staff.save(
                        staff_id=new_leader_id,
                        team_id=team.id,
                        team_code=team.code,
                        role_id=role_leader.id,
                        log_type=StaffLogType.JOIN_TEAM,
                        description='Update team: add new management',
                        user=request.user
                    )

                if update_to_staff_id is not None:
                    staff = Staff.objects.get(pk=update_to_staff_id)
                    staff.role = role_staff
                    staff.save(
                        staff_id=update_to_staff_id,
                        team_id=team.id,
                        team_code=team.code,
                        role_id=role_staff.id,
                        log_type=StaffLogType.UPDATE_ROLE,
                        description='Update team: demote to staff',
                        user=request.user
                    )

                if update_to_leader_id is not None:
                    staff = Staff.objects.get(pk=update_to_leader_id)
                    staff.role = role_leader
                    staff.save(
                        staff_id=update_to_leader_id,
                        team_id=team.id,
                        team_code=team.code,
                        role_id=role_leader.id,
                        log_type=StaffLogType.UPDATE_ROLE,
                        description='Update team: promote to management',
                        user=request.user
                    )

                team.name = name
                team.type = type
                team.description = description
                team.updated_by = request.user
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

            StaffCare.objects.filter(staff__in=staffs).delete()

            staffs.update(
                team=None,
                role=None
            )

            self.create_staff_log(
                staff_ids=remove_ids,
                team=team,
                type=StaffLogType.OUT_TEAM,
                role_id=None,
                description='Delete team'
            )

            team.delete(user=request.user)

            return successful_response()

        except Exception as e:
            logging.error('Delete team exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def create_staff_log(self, staff_ids, team, type, role_id, description, user=None):
        try:
            staff_logs = []

            for staff_id in staff_ids:
                staff_logs.append(StaffLog(
                    staff_id=staff_id,
                    team_id=team.id,
                    team_code=team.code,
                    type=type,
                    role_id=role_id,
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

    code = request.GET.get('code', None)

    if code is not None and code != '':
        queryset = queryset.filter(Q(name__icontains=code) | Q(code__icontains=code))

    queryset = queryset.order_by('name')[0:settings.PAGINATE_BY]

    data = [{'id': team['id'], 'name': team['name'] + ' - ' + team['code']} for team in queryset]

    return successful_response(data)
