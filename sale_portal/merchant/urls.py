from django.conf.urls import url
from django.conf import settings

from .views import index, detail

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^(?P<pk>[0-9]+)/detail/$', detail, name='detail'),
    ]
else:
    urlpatterns = [
        url(r'^$', index, name='index'),
    ]