from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers
from .views import GroupViewSet

router = routers.DefaultRouter()
router.register(r'', GroupViewSet, 'Group')

url_login_patterns = [
    url(r'^', obtain_jwt_token, name='login'),
]
url_account_patterns = [
    url(r'^group/', include(router.urls), name='Restful API Group'),
]
