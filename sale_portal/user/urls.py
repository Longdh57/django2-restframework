from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers
from .views import GroupViewSet, list_groups, PermissionViewSet, model_permissions
from . import views

router_groups = routers.DefaultRouter()
router_groups.register(r'', GroupViewSet, 'Group')

router_permissions = routers.DefaultRouter()
router_permissions.register(r'', PermissionViewSet, 'Permission')


url_login_patterns = [
    url(r'^$', obtain_jwt_token, name='login'),
    url(r'social/jwt_user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialJWTUserAuthView.as_view(),
        name='login_social_jwt_user'),
]
url_account_patterns = [
    url(r'^groups/', include(router_groups.urls), name='Restful API Group'),
    url(r'^groups/list', list_groups, name='get_list_groups'),
    url(r'^permissions/', include(router_permissions.urls), name='List view permission'),
    url(r'^model-permissions/', model_permissions, name='get_model_permissions'),
]
