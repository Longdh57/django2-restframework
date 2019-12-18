import pytest
from mixer.backend.django import mixer

from sale_portal.team.models import Team, TeamLog
from sale_portal.team import TeamType, TeamLogType

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestTeamModel:
    pytestmark = pytest.mark.django_db

    def test_create_team(self):
        team = mixer.blend(Team, name='Team Ha Noi', code='HN1')
        assert team.type == 0

    def create_team_duplicate_code(self):
        try:
            mixer.blend(Team, name='Team Ha Noi', code='HN1')
            mixer.blend(Team, name='Team Ha Nang', code='HN1')
        except Exception as e:
            raise Exception(e)

    def test_create_team_duplicate_code(self):
        with pytest.raises(Exception):
            assert self.create_team_duplicate_code()


@pytest.mark.django_db
class TestTeamLogModel:
    pytestmark = pytest.mark.django_db

    def test_log_action_create_team(self):
        team = Team.objects.create(
            name='Team Ha Noi',
            code='HN1'
        )
        team_log = TeamLog.objects.filter(new_data__icontains=team.code).first()
        assert team_log is not None

    def test_log_action_update_team(self):
        team = mixer.blend(Team, name='Team HCM', code='HCM1')
        team.type = TeamType.TEAM_CHAIN
        team.save()
        team_log = TeamLog.objects.filter(team_id=team.id).order_by('-created_date').first()
        assert team_log.type == TeamLogType.UPDATED

    def test_log_action_delete_team(self):
        team_created = mixer.blend(Team, name='Team DN', code='DN1')
        team_id = team_created.id
        team_created.delete()
        team_log = TeamLog.objects.filter(team_id=team_id).order_by('-created_date').first()
        assert team_log.type == TeamLogType.DELETED
