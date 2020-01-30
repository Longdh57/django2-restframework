from django.conf.urls import url, include

from .views import AreaViewSet, list_areas

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', AreaViewSet, 'Area')

urlpatterns = [
    url(r'^', include(router.urls), name='Restful API Area'),
    url(r'^list', list_areas, name='get_list_areas'),
]
