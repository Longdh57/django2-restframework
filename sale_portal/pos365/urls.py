from django.conf.urls import url, include

from .views import Pos365ViewSet, list_contract_durations

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', Pos365ViewSet, 'Pos365')

urlpatterns = [
    url(r'^', include(router.urls), name='Restful API Pos365'),
    url(r'^list-contract-durations', list_contract_durations, name='get_list_contract_durations'),
]
