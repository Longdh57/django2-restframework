from django.conf.urls import url, include
from rest_framework import routers

from .views import CronjobLogViewSet, getAllJobName, runJobManual

router = routers.DefaultRouter()
router.register(r'', CronjobLogViewSet, 'CronjobLog')

urlpatterns = [
    url(r'^job-name', getAllJobName),
    url(r'^run-job', runJobManual),
    url(r'^', include(router.urls), name='Restful API Area'),
]
