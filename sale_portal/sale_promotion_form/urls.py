from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from .views import SalePromotionViewSet, import_view, export, get_list_titles, reset_data

router = routers.DefaultRouter()
router.register(r'', SalePromotionViewSet, 'SalePromotion')
urlpatterns = [
    url(r'^', include(router.urls), name='SalePromotion'),
    url(r'^import', import_view, name='import'),
    url(r'^export', export, name='export_data_sale_promotion'),
    url(r'^list-title', get_list_titles, name='get_list_titles'),
    url(r'^reset', reset_data, name='reset_data'),
]
