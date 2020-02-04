from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from sale_portal.merchant.views import list_merchants
from .views import SaleReportViewSet, SaleReportStatisticViewSet, list_draff, export_excel

router = routers.DefaultRouter()
router.register(r'', SaleReportViewSet, 'SaleReport')

router_statistic = routers.DefaultRouter()
router_statistic.register(r'', SaleReportStatisticViewSet, 'SaleReportStatistic')

urlpatterns = [
    url(r'^statistic', include(router_statistic.urls), name='SaleReportStatistic'),
    url(r'^list-draff', list_draff, name='list_draff'),
    url(r'^export-statistic-to-excel', export_excel, name='export_excel'),
    url(r'^', include(router.urls), name='SaleReport'),
]
