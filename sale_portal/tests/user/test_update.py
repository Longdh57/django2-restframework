import json
import pytest
from django.contrib.auth.models import Group

from mixer.backend.django import mixer
from django.test import RequestFactory

from sale_portal.area.models import Area
from sale_portal.staff import StaffTeamRoleType
from sale_portal.user import ROLE_SALE_MANAGER, ROLE_SALE_ADMIN, ROLE_SALE_LEADER, ROLE_SALE
from sale_portal.user.models import User
from sale_portal.team.models import Team, TeamType
from sale_portal.staff.models import Staff
from sale_portal.user.views import UserViewSet


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

    staff = mixer.blend(
        Staff,
        staff_code='SP_STAFF',
        full_name='staff',
        email='staff@vnpay.vn',
        status='1',
        created_by=user,
        updated_by=user,
        team=team,
        role=StaffTeamRoleType.TEAM_STAFF
    )

    leader = mixer.blend(
        Staff,
        staff_code='SP_LEADER',
        full_name='leader',
        email='leader@vnpay.vn',
        status='1',
        created_by=user,
        updated_by=user,
        team=team,
        role=StaffTeamRoleType.TEAM_MANAGEMENT
    )

    admin = mixer.blend(
        User,
        username='user_admin',
        is_staff=True,
        is_superuser=True
    )

    area = Area.objects.get(pk=1)

    sale_manager = mixer.blend(
        User,
        username='user_sale_manager',
        is_staff=True,
        is_superuser=False,
        is_area_manager=True
    )
    group_sale_manager = Group.objects.filter(name=ROLE_SALE_MANAGER)
    sale_manager.groups.set(group_sale_manager)
    sale_manager.area_set.add(area)

    sale_admin = mixer.blend(
        User,
        username='user_sale_admin',
        is_staff=True,
        is_superuser=False,
        is_sale_admin=True
    )
    group_sale_admin = Group.objects.filter(name=ROLE_SALE_ADMIN)
    sale_admin.groups.set(group_sale_admin)
    sale_admin.area_set.add(area)

    sale_leader = mixer.blend(
        User,
        username='user_sale_leader',
        is_staff=True,
        is_superuser=False,
        email='leader@vnpay.vn',
    )
    group_sale_leader = Group.objects.filter(name=ROLE_SALE_LEADER)
    sale_leader.groups.set(group_sale_leader)

    sale = mixer.blend(
        User,
        username='user_sale',
        is_staff=True,
        is_superuser=False,
        email='staff@vnpay.vn',
    )
    group_sale = Group.objects.filter(name=ROLE_SALE)
    sale.groups.set(group_sale)

    return {
        'user': user,
        'user_tests': [admin, sale_manager, sale_admin, sale_leader, sale]
    }


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def data(request):
    is_active = request.param.get('is_active')
    role_name = request.param.get('role_name')
    area_ids = request.param.get('area_ids')
    user_permissions = request.param.get('user_permissions')
    return {
        'is_active': is_active if is_active is not None else 'false',
        'role_name': role_name if role_name is not None else 'SALE',
        'area_ids': area_ids if area_ids is not None else [],
        'user_permissions': user_permissions if user_permissions is not None else []
    }


@pytest.fixture
def status_code(request):
    return request.param


@pytest.fixture
def response_message(request):
    return request.param


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [({}, 404, 'USER NOT FOUND')], indirect=True)
def test_user_not_found(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    response = UserViewSet().update(request=request, pk=0)

    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [
                             ({'is_active': ''}, 400, 'status user not valid'),
                             ({'is_active': True}, 400, 'status user not valid'),
                             ({'is_active': 'True'}, 400, 'status user not valid'),
                             ({'is_active': 1}, 400, 'status user not valid'),
                             ({'role_name': ''}, 400, 'role_name not valid'),
                             ({'role_name': 1}, 400, 'role_name not valid'),
                             ({'role_name': 'role_user'}, 404, 'GROUP NOT FOUND'),
                             ({'user_permissions': ''}, 400, 'List user-permission not valid'),
                             ({'user_permissions': 'test'}, 400, 'List user-permission not valid'),
                             ({'user_permissions': 1}, 400, 'List user-permission not valid'),
                             ({'user_permissions': [0, 1, 2, 3]}, 404, 'PERMISSION NOT FOUND'),
                             ({'user_permissions': [0, 1, 2, 3, 'a']}, 500, 'INTERNAL SERVER ERROR'),
                             ({'role_name': ROLE_SALE_MANAGER,
                               'area_ids': ''}, 400, 'List Area not valid'),
                             ({'role_name': ROLE_SALE_MANAGER,
                               'area_ids': 'test'}, 400, 'List Area not valid'),
                             ({'role_name': ROLE_SALE_MANAGER,
                               'area_ids': 1}, 400, 'List Area not valid'),
                             ({'role_name': ROLE_SALE_MANAGER,
                               'area_ids': [0, 1, 2, 3]}, 404, 'AREA NOT FOUND'),
                             ({'role_name': ROLE_SALE_MANAGER,
                               'area_ids': [0, 1, 2, 3, 'a']}, 500, 'INTERNAL SERVER ERROR'),
                         ], indirect=True)
def test_update_data_invalid(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    response = UserViewSet().update(request=request, pk=1)

    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [({'is_active': 'true',
                            'role_name': 'admin',
                            'area_ids': [1],
                            'user_permissions': [1]
                            }, 200, 'SUCCESS')], indirect=True)
def test_update_to_admin(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    for user_test in test_data['user_tests']:
        response = UserViewSet().update(request=request, pk=user_test.id)

        user = User.objects.get(pk=user_test.id)

        assert user.is_superuser
        assert not user.is_area_manager
        assert not user.is_sale_admin
        assert user.groups.count() == 0
        assert user.area_set.count() == 0
        assert response.status_code == status_code
        assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [({'is_active': 'true',
                            'role_name': 'sale manager',
                            'area_ids': [2],
                            'user_permissions': [1]
                            }, 200, 'SUCCESS')], indirect=True)
def test_update_to_sale_manager(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    for user_test in test_data['user_tests']:
        response = UserViewSet().update(request=request, pk=user_test.id)

        user = User.objects.get(pk=user_test.id)

        assert not user.is_superuser
        assert user.is_area_manager
        assert not user.is_sale_admin
        assert user.groups.count() == 1 and user.groups.first().name == ROLE_SALE_MANAGER
        assert user.area_set.count() == 1 and user.area_set.first().id == 2
        assert response.status_code == status_code
        assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [({'is_active': 'true',
                            'role_name': 'sale admin',
                            'area_ids': [2],
                            'user_permissions': [1]
                            }, 200, 'SUCCESS')], indirect=True)
def test_update_to_sale_admin(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    for user_test in test_data['user_tests']:
        response = UserViewSet().update(request=request, pk=user_test.id)

        user = User.objects.get(pk=user_test.id)

        assert not user.is_superuser
        assert not user.is_area_manager
        assert user.is_sale_admin
        assert user.groups.count() == 1 and user.groups.first().name == ROLE_SALE_ADMIN
        assert user.area_set.count() == 1 and user.area_set.first().id == 2
        assert response.status_code == status_code
        assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [({'is_active': 'true',
                            'role_name': 'sale leader',
                            'area_ids': [2],
                            'user_permissions': [1]
                            }, 200, 'SUCCESS')], indirect=True)
def test_update_to_sale_leader(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    for user_test in test_data['user_tests']:
        response = UserViewSet().update(request=request, pk=user_test.id)

        user = User.objects.get(pk=user_test.id)

        assert not user.is_superuser
        assert not user.is_area_manager
        assert not user.is_sale_admin
        assert user.groups.count() == 1 and user.groups.first().name == ROLE_SALE_LEADER
        assert user.area_set.count() == 0
        assert response.status_code == status_code
        assert response_message in str(json.loads(response.content))


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [({'is_active': 'true',
                            'role_name': 'sale',
                            'area_ids': [2],
                            'user_permissions': [1]
                            }, 200, 'SUCCESS')], indirect=True)
def test_update_to_sale(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'PUT'
    request.body = json.dumps(data)

    for user_test in test_data['user_tests']:
        response = UserViewSet().update(request=request, pk=user_test.id)

        user = User.objects.get(pk=user_test.id)

        assert not user.is_superuser
        assert not user.is_area_manager
        assert not user.is_sale_admin
        assert user.groups.count() == 1 and user.groups.first().name == ROLE_SALE
        assert user.area_set.count() == 0
        assert response.status_code == status_code
        assert response_message in str(json.loads(response.content))
