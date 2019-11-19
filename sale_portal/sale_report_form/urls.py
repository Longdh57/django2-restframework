from django.conf.urls import url
from django.conf import settings

from .views import create

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^create/$', create, name='detail'),
    ]
else:
    urlpatterns = [
    ]
