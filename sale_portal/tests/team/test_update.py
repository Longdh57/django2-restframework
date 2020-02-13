import json
import pytest

from mixer.backend.django import mixer
from django.test import RequestFactory

from sale_portal.staff import StaffTeamRoleType
from sale_portal.user.models import User
from sale_portal.team.views import TeamViewSet
from sale_portal.team.models import Team, TeamLog, TeamType, TeamLogType
from sale_portal.staff.models import Staff, StaffLog, StaffLogType


@pytest.fixture
def test_data(db):
    user = mixer.blend(User, username='test_superuser', is_staff=True, is_superuser=True)
    team = mixer.blend(
        Team,
        name='Team Test',
        code='TEAM_TEST',
        type=TeamType.TEAM_SALE,
        area=None,
        created_by=user,
        updated_by=user
    )

    role_staff = StaffTeamRoleType.TEAM_STAFF
    role_manager = StaffTeamRoleType.TEAM_MANAGEMENT

    Staff.objects.filter(pk=1149).update(team=team, role=role_staff)
    Staff.objects.filter(pk=1160).update(team=team, role=role_manager)

    return {'user': user, 'team': team}


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def data(request):
    name = request.param.get('name')
    type = request.param.get('type')
    staffs = request.param.get('staffs')
    return {
        'name': name if name is not None else 'Team Test with Pytest',
        'type': type if type is not None else 1,
        'description': 'Mo ta team Test',
        'staffs': staffs if staffs is not None else [
            {
                'id': 1149,
                'role': 'TEAM_STAFF'
            },
            {
                'id': 1160,
                'role': 'TEAM_MANAGEMENT'
            }
        ]
    }


@pytest.fixture
def status_code(request):
    return request.param


@pytest.fixture
def response_message(request):
    return request.param


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [({'staffs': [
                             {
                                 'id': 1168,
                                 'role': 'TEAM_STAFF'
                             },
                             {
                                 'id': 1194,
                                 'role': 'TEAM_STAFF'
                             },
                             {
                                 'id': 1185,
                                 'role': 'TEAM_MANAGEMENT'
                             }
                         ]}, 404, 'TEAM NOT FOUND')], indirect=True)
def test_update_team_not_found(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    response = TeamViewSet().update(request=request, pk=1000000)

    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [
                             ({'staffs': 1}, 400, 'staffs Invalid'),
                             ({'name': ''}, 400, 'name Invalid'),
                             ({'type': 100}, 400, 'type Invalid'),
                             ({'name': 'HN5'}, 400, 'name being used by other Team'),
                             ({'staffs': [
                                 {
                                     'id': '1149',
                                     'role': 'TEAM_STAFF'
                                 }
                             ]}, 400, 'staff_id Invalid'),
                             ({'staffs': [
                                 {
                                     'id': 1149,
                                     'role': 'TEAM_MANAGEMENT'
                                 },
                                 {
                                     'id': 1160,
                                     'role': 'TEAM_MANAGEMENT'
                                 }
                             ]}, 400, 'Team chỉ được phép có 1 leader'),
                             ({'staffs': [
                                 {
                                     'id': 1160,
                                     'role': 'TEAM_MANAGEMENTXX'
                                 }
                             ]}, 400, 'staff_role Invalid'),
                             ({'staffs': [
                                 {
                                     'id': 10000000,
                                     'role': 'TEAM_STAFF'
                                 }
                             ]}, 404, 'staff_id 10000000 not found'),
                             ({'staffs': [
                                 {
                                     'id': 1191,
                                     'role': 'TEAM_MANAGEMENT'
                                 }
                             ]}, 400, 'đang thuộc team khác'),
                         ], indirect=True)
def test_update_data_invalid(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    response = TeamViewSet().update(request=request, pk=test_data['team'].id)

    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [({'staffs': [
                             {
                                 'id': 1168,
                                 'role': 'TEAM_STAFF'
                             },
                             {
                                 'id': 1194,
                                 'role': 'TEAM_STAFF'
                             },
                             {
                                 'id': 1185,
                                 'role': 'TEAM_MANAGEMENT'
                             }
                         ]}, 200, 'SUCCESS')], indirect=True)
def test_update_success(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    response = TeamViewSet().update(request=request, pk=test_data['team'].id)

    team = Team.objects.get(pk=test_data['team'].id)
    team_log = TeamLog.objects.filter(team_id=test_data['team'].id, type=TeamLogType.UPDATED).order_by(
        '-created_date').first()

    staff1 = Staff.objects.get(pk=1168)
    staff2 = Staff.objects.get(pk=1185)

    staff_log1 = StaffLog.objects.filter(staff_id=staff1.id).order_by('-created_date').first()
    staff_log2 = StaffLog.objects.filter(staff_id=staff2.id).order_by('-created_date').first()

    role_staff = StaffTeamRoleType.TEAM_STAFF
    role_manager = StaffTeamRoleType.TEAM_MANAGEMENT

    assert team.name == data['name'] and team.type == data['type']
    assert team_log is not None
    assert staff1.team_id == team.id and staff1.role == role_staff
    assert staff2.team_id == team.id and staff2.role == role_manager
    assert staff_log1 is not None and staff_log1.team_id == team.id and staff_log1.role == role_staff
    assert staff_log2 is not None and staff_log2.team_id == team.id and staff_log2.role == role_manager
    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))
