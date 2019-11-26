from django.conf.urls import url, include

from rest_framework import routers

from .views import MerchantViewSet, list_merchants, list_status

router = routers.DefaultRouter()
router.register(r'', MerchantViewSet, 'Merchant')

urlpatterns = [
    url(r'^', include(router.urls), name='Restful API Merchant'),
    url(r'^list', list_merchants, name='get_list_merchants'),
    url(r'^status', list_status, name='get_list_status'),
]
