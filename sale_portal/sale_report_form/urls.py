from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from .views import SaleReportViewSet

router = routers.DefaultRouter()
router.register(r'', SaleReportViewSet, 'SaleReport')
urlpatterns = [
    url(r'^', include(router.urls), name='SaleReport'),
]
