import json
import pytest

from mixer.backend.django import mixer
from django.test import RequestFactory

from sale_portal.user.models import User
from sale_portal.team.views import TeamViewSet
from sale_portal.team.models import Team, TeamLog, TeamLogType
from sale_portal.staff.models import Staff, StaffTeamRole, StaffLog, StaffLogType


@pytest.fixture
def user(db):
    return mixer.blend(User, username='test_superuser', is_staff=True, is_superuser=True)


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def data(request):
    name = request.param.get('name')
    code = request.param.get('code')
    type = request.param.get('type')
    area_id = request.param.get('area_id')
    staffs = request.param.get('staffs')
    return {
        'name': name if name is not None else 'Team Test with Pytest',
        'code': code if code is not None else 'TEAM_TEST',
        'type': type if type is not None else 1,
        'area_id': area_id if area_id is not None else 1,
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
                         [
                             ({'staffs': 1}, 400, 'staffs Invalid'),
                             ({'type': 3}, 400, 'type Invalid'),
                             ({'code': ''}, 400, 'name or code Invalid'),
                             ({'name': ''}, 400, 'name or code Invalid'),
                             ({'area_id': ''}, 400, 'area_id not valid'),
                             ({'area_id': 0}, 404, 'AREA NOT FOUND'),
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
                                     'id': 1149,
                                     'role': 'TEAM_STAFFF'
                                 }
                             ]}, 400, 'staff_role Invalid'),
                             ({'staffs': [
                                 {
                                     'id': 100000,
                                     'role': 'TEAM_STAFF'
                                 }
                             ]}, 404, 'STAFF NOT FOUND'),
                         ]
    , indirect=True)
def test_create_data_invalid(user, factory, data, status_code, response_message):
    request = factory
    request.user = user
    request.method = 'POST'
    request.body = json.dumps(data)

    response = TeamViewSet().create(request=request)

    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize('data', [{}], indirect=True)
def test_create_success(user, factory, data):
    request = factory
    request.user = user
    request.method = 'POST'
    request.body = json.dumps(data)

    TeamViewSet().create(request=request)

    team = Team.objects.filter(code=data['code']).first()
    team_log = TeamLog.objects.filter(
        new_data__icontains=data['code'], type=TeamLogType.CREATED).first()
    staff = Staff.objects.get(pk=1149)
    staff_log = StaffLog.objects.filter(staff_id=1149, type=StaffLogType.JOIN_TEAM).first()
    role = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()

    assert team.name == data['name'] and team.type == data['type']
    assert staff.team_id == team.id and staff.role_id == role.id
    assert staff_log is not None and staff_log.team_id == team.id
    assert team_log is not None
