from django.conf.urls import url, include

from .views import ExchangePointPos365ViewSet, get_proportion_kpi_team

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', ExchangePointPos365ViewSet, 'ExchangePointPos365')

urlpatterns = [
    url(r'^exchange-point-pos365/', include(router.urls), name='Restful API ExchangePointPos365'),
    url(r'^proportion-kpi-team/', get_proportion_kpi_team, name='Get table ProportionKpiTeam'),
]
