from django.conf.urls import url

from .views import list_shop_for_search, list_recommend_shops

urlpatterns = [
    url(r'^list-shop-for-search/$', list_shop_for_search, name='list_shop_for_search'),
    url(r'^list-recommend-shops/(?P<pk>[0-9]+)/$', list_recommend_shops, name='list_recommend_shops'),
]

