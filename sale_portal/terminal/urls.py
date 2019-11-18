from django.conf.urls import url, include
from django.conf import settings
from rest_framework import routers

from .views import index, TerminalViewSet, detail

router = routers.DefaultRouter()
router.register(r'datatables', TerminalViewSet, 'Terminal')

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^', include(router.urls), name='get_list_terminal_datatables'),
        url(r'^(?P<pk>[0-9]+)/detail/$', detail, name='detail'),
    ]
else:
    urlpatterns = [
        url(r'^$', index, name='index'),
        # url(r'^(?P<pk>[0-9]+)/detail/$', show, name='show'),
    ]
