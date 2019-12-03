from django.conf.urls import url, include

from rest_framework import routers

from .views import TerminalViewSet, list_terminals, list_status, create_shop_from_terminal

router = routers.DefaultRouter()
router.register(r'', TerminalViewSet, 'Terminal')

urlpatterns = [
    url(r'^', include(router.urls), name='Restful API Terminal'),
    url(r'^list', list_terminals, name='get_list_terminals'),
    url(r'^status', list_status, name='get_list_status'),
    url(r'^create-shop-from-terminal', create_shop_from_terminal, name='create_shop_from_terminal'),
]
