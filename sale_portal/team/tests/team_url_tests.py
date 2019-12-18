import json
import pytest

from django.urls import reverse
from django.http import HttpRequest

from mixer.backend.django import mixer

from sale_portal.user.models import User
from sale_portal.team.views import TeamViewSet

pytestmark = pytest.mark.django_db


# @pytest.mark.django_db
# class TestTeamUrl:
#     pytestmark = pytest.mark.django_db
#
#     def create_superuser(self):
#         user = mixer.blend(User, is_staff=True, is_superuser=True)
#         return user
#
#     def test_create_url(self):
#         team = {
#             "code": "DN1",
#             "name": "Da Nang 1",
#             "type": 2,
#             "description": "This is a test description",
#             "staffs": [
#                 {
#                     "id": 1204,
#                     "role": "TEAM_STAFF"
#                 },
#                 {
#                     "id": 1203,
#                     "role": "TEAM_STAFF"
#                 }
#             ]
#         }
#
#         request = HttpRequest()
#         request.method = 'POST'
#         request.user = self.create_superuser()
#         request.content_type = 'application/json'
#         request._body = json.dumps(team)
#
#         response = TeamViewSet().create(request)
#         print(response.body)
#         assert json.loads(response.body)['message'] == 'Invalid body (staff_id Invalid)'


@pytest.mark.django_db
def test_unauthorized_request(api_client):
    url = reverse('api.merchant.get_list_merchants')
    response = api_client.get(url)
    assert response.status_code == 401
