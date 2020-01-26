import json
import pytest

from mixer.backend.django import mixer
from django.test import RequestFactory

from sale_portal.user.models import User
from sale_portal.shop.models import Shop
from sale_portal.team.views import TeamViewSet
from sale_portal.staff_care.models import StaffCare
from sale_portal.team.models import Team, TeamLog, TeamType, TeamLogType
from sale_portal.staff.models import Staff, StaffTeamRole, StaffLog, StaffLogType


@pytest.fixture
def test_data(db):
    user = mixer.blend(User, username='test_superuser', is_staff=True, is_superuser=True)
    team = mixer.blend(Team, name='Team Test', code='TEAM_TEST', type=TeamType.TEAM_SALE, area=None,
                       created_by=user, updated_by=user)

    role_staff = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()
    role_manager = StaffTeamRole.objects.filter(code='TEAM_MANAGEMENT').first()

    Staff.objects.filter(pk=1149).update(team=team, role=role_staff)
    Staff.objects.filter(pk=1160).update(team=team, role=role_manager)

    Shop.objects.get(pk=45092).staff_create(1149)
    Shop.objects.get(pk=39407).staff_create(1160)
    return {'user': user, 'team': team}


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def response_message(request):
    return request.param


@pytest.mark.django_db
@pytest.mark.parametrize('response_message', ['TEAM NOT FOUND'], indirect=True)
def test_delete_not_found(test_data, factory, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'DELETE'

    response = TeamViewSet().destroy(request=request, pk=1000000)

    assert response.status_code == 404
    assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize('response_message', ['SUCCESS'], indirect=True)
def test_delete_success(test_data, factory, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'DELETE'

    response = TeamViewSet().destroy(request=request, pk=test_data['team'].id)

    team_log = TeamLog.objects.filter(team_id=test_data['team'].id).order_by('-created_date').first()

    staff1 = Staff.objects.get(pk=1149)
    staff2 = Staff.objects.get(pk=1160)

    staff_log1 = StaffLog.objects.filter(staff_id=staff1.id).order_by('-created_date').first()
    staff_log2 = StaffLog.objects.filter(staff_id=staff2.id).order_by('-created_date').first()

    count_staff_care_1 = StaffCare.objects.filter(staff=staff1).count()
    count_staff_care_2 = StaffCare.objects.filter(staff=staff2).count()

    assert response_message in str(json.loads(response.content))
    assert team_log is not None and team_log.type == TeamLogType.DELETED
    assert staff_log1 is not None and staff_log1.type == StaffLogType.OUT_TEAM and staff_log1.team_id == test_data[
        'team'].id
    assert staff_log2 is not None and staff_log2.type == StaffLogType.OUT_TEAM and staff_log2.team_id == test_data[
        'team'].id
    assert count_staff_care_1 == 0 and count_staff_care_2 == 0
