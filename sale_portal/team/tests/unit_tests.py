import json
import pytest

from django.test import RequestFactory
from mixer.backend.django import mixer

from sale_portal.user.models import User
from sale_portal.team.views import TeamViewSet
from sale_portal.staff.models import Staff, StaffTeamRole
from sale_portal.team.models import Team


@pytest.mark.django_db
def test_create():
    user = mixer.blend(User, username='test_superuser', is_staff=True, is_superuser=True)
    data = {
        'code': 'LONGTEST1',
        'name': 'Team Long Test 1',
        'type': 2,
        'description': 'Mo ta team long test 1',
        'staffs': [
            {
                'id': 1149,
                'role': 'TEAM_STAFF'
            },
            {
                'id': 1168,
                'role': 'TEAM_STAFF'
            },
            {
                'id': 1160,
                'role': 'TEAM_MANAGEMENT'
            }
        ]
    }
    request = RequestFactory()
    request.method = 'POST'
    request.user = user
    request.body = json.dumps(data)
    team_object = TeamViewSet()
    team_object.create(request=request)

    team = Team.objects.filter(code=data['code']).first()
    staff = Staff.objects.get(pk=1149)
    role = StaffTeamRole.objects.filter(code='TEAM_STAFF').first()

    assert team.name == data['name'] and team.type == data['type']

    assert staff.team_id == team.id and staff.role_id == role.id
