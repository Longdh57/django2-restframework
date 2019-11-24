from django.conf.urls import url, include

from .views import list_teams, TeamViewSet

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', TeamViewSet, 'Team')

urlpatterns = [
    url(r'^', include(router.urls), name='Restful API Team'),
    url(r'^list', list_teams, name='get_list_teams'),
]
