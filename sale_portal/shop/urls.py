from django.conf.urls import url

from .views import list_shop_for_search

urlpatterns = [
    url(r'^list-shop-for-search/$', list_shop_for_search, name='list_shop_for_search'),
]

