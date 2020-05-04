from django.conf.urls import url, include
from rest_framework import routers

from .views import import_sale_shop, import_sale_merchant, StaffCareImportLogViewSet, StaffCareLogViewSet

router = routers.DefaultRouter()
router.register(r'^log', StaffCareLogViewSet, 'StaffCareLog')
router.register(r'^import-log', StaffCareImportLogViewSet, 'StaffCareImportLog')

urlpatterns = [
    url(r'^import-sale-shop', import_sale_shop, name='import_sale_shop'),
    url(r'^import-sale-merchant', import_sale_merchant, name='import_sale_merchant'),
    url(r'', include(router.urls), name='StaffCare'),
]
