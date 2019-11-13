from django.conf.urls import url, include
from django.conf import settings
from rest_framework import routers

from .views import index, MerchantViewSet, detail

router = routers.DefaultRouter()
router.register(r'datatables', MerchantViewSet, 'Merchant')

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^', include(router.urls), name='get_list_merchant'),
        url(r'^(?P<pk>[0-9]+)/detail/$', detail, name='detail'),
    ]
else:
    urlpatterns = [
        url(r'^$', index, name='index'),
    ]