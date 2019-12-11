import pytest
from mixer.backend.django import mixer

from sale_portal.staff.models import Staff, StaffTeamRole

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestStaffTeamRoleClass:
    pytestmark = pytest.mark.django_db

    def test_create_staff_team_role(self):
        role = mixer.blend(StaffTeamRole, code='TEAM_MANAGER')
        assert role.code == 'TEAM_MANAGER'