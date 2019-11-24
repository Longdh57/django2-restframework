from django.conf.urls import url
from django.conf import settings

from .views import store

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^store/$', store, name='store'),
    ]
else:
    urlpatterns = [
    ]
