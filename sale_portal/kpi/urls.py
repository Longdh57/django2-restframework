from django.conf.urls import url

from .views import get_data_kpi_yourself

urlpatterns = [
    url(r'^get-data-kpi-yourself', get_data_kpi_yourself, name='get_data_kpi_yourself'),
]
