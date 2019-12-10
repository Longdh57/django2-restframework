import pytest
from mixer.backend.django import mixer

from sale_portal.team.models import Team, TeamLog
from sale_portal.team import TeamType, TeamLogType

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestClass:
    pytestmark = pytest.mark.django_db

    def test_create_team(self):
        team = mixer.blend(Team, name='Team Ha Noi', code='HN1')
        assert team.type == 0

    def test_log_action_create_team(self):
        team = Team.objects.create(
            name='Team Da Nang',
            code='DN1'
        )
        team_log = TeamLog.objects.filter(new_data__icontains=team.code).first()
        assert team_log is not None

    def test_log_action_update_team(self):
        team = mixer.blend(Team, name='Team HCM', code='HCM1')

        team.type = TeamType.TEAM_CHAIN
        team.save()

        team_log = TeamLog.objects.filter(team_id=team.id).order_by('-created_date').first()
        assert team_log.type == TeamLogType.UPDATED
