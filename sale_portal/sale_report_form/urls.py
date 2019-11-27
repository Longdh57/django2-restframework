from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from .views import store, SaleReportViewSet

router = routers.DefaultRouter()
router.register(r'', SaleReportViewSet, 'SaleReport')
urlpatterns = [
    url(r'^$', include(router.urls), name='Restful API SaleReport'),
    url(r'^store/$', store, name='store'),
]
