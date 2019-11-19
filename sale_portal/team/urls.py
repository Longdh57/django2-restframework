from django.conf.urls import url, include
from django.conf import settings
from .views import list_teams, TeamViewSet

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'datatables', TeamViewSet, 'Team')

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^', include(router.urls), name='get_list_team_datatables'),
        url(r'^list-teams/$', list_teams, name='get_list_teams'),
    ]
else:
    urlpatterns = [
        # url(r'^$', index, name='index'),
    ]
