from django.conf.urls import url, include
from django.conf import settings
from rest_framework import routers

from .views import index, MerchantViewSet, show, list_merchants, list_status

router = routers.DefaultRouter()
router.register(r'', MerchantViewSet, 'Merchant')

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^', include(router.urls), name='Restful API Merchant'),
        url(r'^list', list_merchants, name='get_list_merchants'),
        url(r'^status', list_status, name='get_list_status'),
    ]
else:
    urlpatterns = [
        url(r'^$', index, name='index'),
        url(r'^(?P<pk>[0-9]+)/detail/$', show, name='show'),
    ]
