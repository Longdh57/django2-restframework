from django.conf.urls import url, include
from rest_framework import routers

from .views import CronjobLogViewSet, getAllJobName, runJobManual, get_job_status

router = routers.DefaultRouter()
router.register(r'', CronjobLogViewSet, 'CronjobLog')

urlpatterns = [
    url(r'^job-name', getAllJobName),
    url(r'^run-job', runJobManual),
    url(r'^job-status', get_job_status),
    url(r'^', include(router.urls), name='Restful API Area'),
]
