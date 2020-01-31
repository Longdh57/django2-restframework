from django.conf.urls import url, include

from .views import list_provinces, list_districts, list_wards


urlpatterns = [
    url(r'^provinces', list_provinces, name='get_list_provinces'),
    url(r'^districts', list_districts, name='get_list_districts'),
    url(r'^wards', list_wards, name='get_list_wards'),
]
