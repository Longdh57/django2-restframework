from django.conf.urls import url, include
from django.conf import settings
from .views import list_staffs

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    urlpatterns = [
        url(r'^list-staffs/$', list_staffs, name='get_list_staffs'),
    ]
else:
    urlpatterns = [
        # url(r'^$', index, name='index'),
    ]
