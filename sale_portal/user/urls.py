from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers
from .views import GroupViewSet
from . import views

router = routers.DefaultRouter()
router.register(r'', GroupViewSet, 'Group')

url_login_patterns = [
    url(r'^$', obtain_jwt_token, name='login'),
    url(r'social/jwt_user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialJWTUserAuthView.as_view(),
        name='login_social_jwt_user'),
]
url_account_patterns = [
    url(r'^group/', include(router.urls), name='Restful API Group'),
]
