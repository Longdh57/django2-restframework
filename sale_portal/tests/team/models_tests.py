import pytest
from mixer.backend.django import mixer

from sale_portal.team.models import Team, TeamLog
from sale_portal.team import TeamType, TeamLogType

@pytest.mark.django_db
def test_create_team():
    team = Team.objects.create(
        name='Team Test',
        code='TEST_TEAM',
    )
    assert team.type == 0


@pytest.mark.django_db
def test_log_action_create_team():
    team = Team.objects.create(name='Team Ha Noi', code='HN1')
    team_log = TeamLog.objects.filter(new_data__icontains=team.code).first()
    assert team_log is not None


@pytest.mark.django_db
def test_log_action_update_team():
    team = Team.objects.create(name='Team Test', code='TEST_TEAM', area=None)
    team.type = TeamType.TEAM_CHAIN
    team.save()
    team_log = TeamLog.objects.filter(team_id=team.id).order_by('-created_date').first()
    assert team_log.type == TeamLogType.UPDATED


@pytest.mark.django_db
def test_log_action_delete_team():
    team_created = mixer.blend(Team, name='Team DN', code='DN1', area=None)
    team_id = team_created.id
    team_created.delete()
    team_log = TeamLog.objects.filter(team_id=team_id).order_by('-created_date').first()
    assert team_log.type == TeamLogType.DELETED
