from django.conf.urls import url, include

from .views import AreaViewSet, list_areas, update_proportion_kpi_s73

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', AreaViewSet, 'Area')

urlpatterns = [
    url(r'^list', list_areas, name='get_list_areas'),
    url(r'^update-proportion-kpi-s73/(?P<pk>[0-9]+)', update_proportion_kpi_s73, name='update_proportion_kpi_s73'),
    url(r'^', include(router.urls), name='Restful API Area'),
]
