from django.conf.urls import url, include
from rest_framework import routers

from .views import import_sale_shop, import_sale_merchant

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^import-sale-shop', import_sale_shop, name='import_sale_shop'),
    url(r'^import-sale-merchant', import_sale_merchant, name='import_sale_merchant'),
]

