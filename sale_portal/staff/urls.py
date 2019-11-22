from django.conf.urls import url, include
from django.conf import settings
from .views import list_staffs, StaffViewSet, change_staff_team

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', StaffViewSet, 'Staff')

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^', include(router.urls), name='Restful API Staff'),
        url(r'^list', list_staffs, name='get_list_staffs'),
        url(r'^team', change_staff_team, name='change_staff_team'),
    ]
else:
    urlpatterns = [
        # url(r'^$', index, name='index'),
    ]
