from django.conf.urls import url, include
from rest_framework import routers

from .views import import_sale_shop, import_sale_merchant, StaffCareImportLogViewSet

router = routers.DefaultRouter()
router.register(r'', StaffCareImportLogViewSet, 'StaffCareImportLog')

urlpatterns = [
    url(r'^import-sale-shop', import_sale_shop, name='import_sale_shop'),
    url(r'^import-sale-merchant', import_sale_merchant, name='import_sale_merchant'),
    url(r'^import-log', include(router.urls), name='StaffCareImportLog'),
]
