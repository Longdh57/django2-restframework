from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from .views import SalePromotionViewSet, import_view, export, get_list_titles, reset_data, list_promotion_shops_for_search

router = routers.DefaultRouter()
router.register(r'', SalePromotionViewSet, 'SalePromotion')
urlpatterns = [
    url(r'^list-promotion-shop-for-search', list_promotion_shops_for_search, name='list_promotion_shop_for_search'),
    url(r'^(?P<pk>[0-9]+)/reset', reset_data, name='reset_data'),
    url(r'^', include(router.urls), name='SalePromotion'),
    url(r'^import', import_view, name='import'),
    url(r'^export', export, name='export_data_sale_promotion'),
    url(r'^list-title', get_list_titles, name='get_list_titles'),
]
