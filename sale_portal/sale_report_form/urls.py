from django.conf.urls import url
from django.conf import settings

from .views import create, open_new

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^create/$', create, name='detail'),
        url(r'^open-new/$', open_new, name='open_new'),
    ]
else:
    urlpatterns = [
    ]
