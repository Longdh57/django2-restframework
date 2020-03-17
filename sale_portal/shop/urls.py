from django.conf.urls import url, include
from rest_framework import routers

from .views import list_shop_for_search, list_recommend_shops, ShopViewSet, get_count_shop_30_days_before, export, \
    create_from_terminal, assign_ter_to_shop, ShopLogViewSet

router = routers.DefaultRouter()
router.register(r'^shop-log', ShopLogViewSet, 'ShopLog')
router.register(r'', ShopViewSet, 'Shop')

urlpatterns = [
    url(r'^list-shop-for-search', list_shop_for_search, name='list_shop_for_search'),
    url(r'^create-from-terminal', create_from_terminal, name='create_from_terminal'),
    url(r'^assign-ter-to-shop', assign_ter_to_shop, name='assign_ter_to_shop'),
    url(r'^list-recommend-shops/(?P<pk>[0-9]+)', list_recommend_shops, name='list_recommend_shops'),
    url(r'^export', export, name='export_data_shop'),
    url(r'^count-shop-30-days-before/$', get_count_shop_30_days_before, name='count_shop_30_days_before'),
    url(r'^', include(router.urls), name='Restful API Shop'),
]
