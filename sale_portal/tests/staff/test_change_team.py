import json
import pytest

from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import APIRequestFactory

from sale_portal.staff import StaffTeamRoleType
from sale_portal.user.models import User
from sale_portal.staff.views import change_staff_team
from sale_portal.team.models import Team, TeamType
from sale_portal.staff.models import Staff, StaffLog, StaffLogType


@pytest.fixture
def test_data(db):
    user = mixer.blend(User, username='test_superuser', is_staff=True, is_superuser=True)
    team_before = mixer.blend(
        Team,
        name='Team Test 1',
        code='TEAM_TEST_1',
        type=TeamType.TEAM_SALE,
        area=None,
        created_by=user,
        updated_by=user
    )

    team_after = mixer.blend(
        Team,
        name='Team Test 2',
        code='TEAM_TEST_2',
        type=TeamType.TEAM_SALE,
        area=None,
        created_by=user,
        updated_by=user
    )

    staff_have_team = mixer.blend(
        Staff,
        staff_code='SP_STAFF_1',
        full_name='user_test1',
        email='tester1@vnpay.vn',
        status='1',
        created_by=user,
        updated_by=user,
        team=team_before,
        role=StaffTeamRoleType.TEAM_STAFF
    )

    staff_no_team = mixer.blend(
        Staff,
        staff_code='SP_STAFF_2',
        full_name='user_test2',
        email='tester2@vnpay.vn',
        status='1',
        created_by=user,
        updated_by=user,
        team=None,
        role=StaffTeamRoleType.FREELANCE_STAFF
    )

    return {'user': user, 'team_before_id': team_before.id, 'team_after_id': team_after.id,
            'staff_have_team_id': staff_have_team.id, 'staff_no_team_id': staff_no_team.id}


@pytest.fixture
def data(request):
    staff_id = request.param.get('staff_id')
    team_id = request.param.get('team_id')
    return {
        'staff_id': staff_id if staff_id is not None else 1,
        'team_id': team_id if team_id is not None else 1,
    }


@pytest.fixture
def status_code(request):
    return request.param


@pytest.fixture
def response_message(request):
    return request.param


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [({'staff_id': 1,
                            'team_id': 0
                            }, 404, 'TEAM NOT FOUND'),
                          ({'staff_id': 0,
                           'team_id': 1
                           }, 404, 'STAFF NOT FOUND')], indirect=True)
def test_update_team_not_found(test_data, data, status_code, response_message):
    request = APIRequestFactory().post('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
def test_add_team_invalid(test_data):
    # ------------------------------ case 1 ----------------------------------
    data = {
        'staff_id': test_data['staff_have_team_id'],
        'team_id': test_data['team_after_id']
    }
    request = APIRequestFactory().post('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Staff đang thuộc 1 Team khác' in str(json.loads(response.content))

    # ------------------------------ case 1 ----------------------------------

    data = {
        'staff_id': test_data['staff_have_team_id'],
        'team_id': test_data['team_before_id']
    }
    request = APIRequestFactory().post('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Staff đã thuộc team này từ trước' in str(json.loads(response.content))


@pytest.mark.django_db
def test_update_team_invalid(test_data):
    # ------------------------------ case 1 ----------------------------------
    data = {
        'staff_id': test_data['staff_no_team_id'],
        'team_id': test_data['team_after_id']
    }
    request = APIRequestFactory().put('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Staff đang không thuộc team nào, không thể chuyển Team' in str(json.loads(response.content))

    # ------------------------------ case 1 ----------------------------------

    data = {
        'staff_id': test_data['staff_have_team_id'],
        'team_id': test_data['team_before_id']
    }
    request = APIRequestFactory().put('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Staff đã thuộc team này từ trước' in str(json.loads(response.content))


@pytest.mark.django_db
def test_delete_team_invalid(test_data):
    # ------------------------------ case 1 ----------------------------------
    data = {
        'staff_id': test_data['staff_no_team_id'],
        'team_id': test_data['team_after_id']
    }
    request = APIRequestFactory().delete('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Staff đang không thuộc team nào, không thể xóa Team' in str(json.loads(response.content))

    # ------------------------------ case 1 ----------------------------------

    data = {
        'staff_id': test_data['staff_have_team_id'],
        'team_id': test_data['team_after_id']
    }
    request = APIRequestFactory().delete('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Staff không thuộc team hiện tại' in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('status_code', 'response_message'),
                         [(200, 'SUCCESS')], indirect=True)
def test_add_team_success(test_data, status_code, response_message):
    data = {
        'staff_id': test_data['staff_no_team_id'],
        'team_id': test_data['team_after_id']
    }

    request = APIRequestFactory().post('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    staff = Staff.objects.get(pk=test_data['staff_no_team_id'])

    staff_log = StaffLog.objects.filter(staff_id=staff.id).order_by('-created_date').first()

    role_staff = StaffTeamRoleType.TEAM_STAFF

    assert staff.team.id == test_data['team_after_id'] and staff.role == role_staff
    assert staff_log is not None
    assert staff_log is not None and staff_log.team_id == test_data['team_after_id'] and staff_log.role == role_staff and staff_log.type == StaffLogType.JOIN_TEAM
    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('status_code', 'response_message'),
                         [(200, 'SUCCESS')], indirect=True)
def test_change_team_success(test_data, status_code, response_message):
    data = {
        'staff_id': test_data['staff_have_team_id'],
        'team_id': test_data['team_after_id']
    }

    request = APIRequestFactory().put('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    staff = Staff.objects.get(pk=test_data['staff_have_team_id'])

    staff_log_out = StaffLog.objects.filter(staff_id=staff.id, type=StaffLogType.OUT_TEAM).order_by('-created_date').first()
    staff_log_join = StaffLog.objects.filter(staff_id=staff.id, type=StaffLogType.JOIN_TEAM).order_by('-created_date').first()

    role_staff = StaffTeamRoleType.TEAM_STAFF
    role_freelance_staff = StaffTeamRoleType.FREELANCE_STAFF

    assert staff.team.id == test_data['team_after_id'] and staff.role == role_staff
    assert staff_log_out is not None and staff_log_out.team_id == test_data['team_before_id']\
           and staff_log_out.role == role_freelance_staff
    assert staff_log_join is not None and staff_log_join.team_id == test_data['team_after_id']\
           and staff_log_join.role == role_staff
    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('status_code', 'response_message'),
                         [(200, 'SUCCESS')], indirect=True)
def test_delete_team_success(test_data, status_code, response_message):
    data = {
        'staff_id': test_data['staff_have_team_id'],
        'team_id': test_data['team_before_id']
    }

    request = APIRequestFactory().delete('/api/staffs/team', data=json.dumps(data), content_type='application/json')
    request.user = test_data['user']

    response = change_staff_team(request=request)

    staff = Staff.objects.get(pk=test_data['staff_have_team_id'])

    staff_log = StaffLog.objects.filter(staff_id=staff.id).order_by('-created_date').first()

    role_freelance_staff = StaffTeamRoleType.FREELANCE_STAFF

    assert staff.team is None and staff.role == role_freelance_staff
    assert staff_log is not None and staff_log.team_id == test_data['team_before_id']\
           and staff_log.role == role_freelance_staff and staff_log.type == StaffLogType.OUT_TEAM
    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))
