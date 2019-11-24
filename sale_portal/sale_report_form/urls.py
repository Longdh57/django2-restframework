from django.conf.urls import url

from .views import create, open_new

urlpatterns = [
    url(r'^create/$', create, name='detail'),
    url(r'^open-new/$', open_new, name='open_new'),
]
