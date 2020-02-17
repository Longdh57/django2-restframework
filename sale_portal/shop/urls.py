from django.conf.urls import url, include
from rest_framework import routers

from .views import list_shop_for_search, list_recommend_shops, ShopViewSet, get_count_shop_30_days_before

router = routers.DefaultRouter()
router.register(r'', ShopViewSet, 'Shop')

urlpatterns = [
    url(r'^list-shop-for-search', list_shop_for_search, name='list_shop_for_search'),
    url(r'^list-recommend-shops/(?P<pk>[0-9]+)', list_recommend_shops, name='list_recommend_shops'),
    url(r'^count-shop-30-days-before/$', get_count_shop_30_days_before, name='count_shop_30_days_before'),
    url(r'^', include(router.urls), name='Restful API Shop'),
]

