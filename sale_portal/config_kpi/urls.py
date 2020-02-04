from django.conf.urls import url, include

from .views import ExchangePointPos365ViewSet, get_proportion_kpi_team, \
    list_type_proportion_kpi_team, update_proportion_kpi_team

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', ExchangePointPos365ViewSet, 'ExchangePointPos365')

urlpatterns = [
    url(r'^proportion-kpi-team/list-type', list_type_proportion_kpi_team, name='Get list type ProportionKpiTeam'),
    url(r'^proportion-kpi-team/(?P<pk>[0-9]+)', update_proportion_kpi_team, name='Update ProportionKpiTeam'),
    url(r'^proportion-kpi-team/', get_proportion_kpi_team, name='Get list ProportionKpiTeam'),
    url(r'^exchange-point-pos365/', include(router.urls), name='Restful API ExchangePointPos365'),
]
