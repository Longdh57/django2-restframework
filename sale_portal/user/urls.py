from django.conf.urls import url, include
from rest_framework import routers
from .views import GroupViewSet, list_groups, PermissionViewSet, model_permissions, UserViewSet, user_info
from . import views

router_users = routers.DefaultRouter()
router_users.register(r'', UserViewSet, 'User')

router_groups = routers.DefaultRouter()
router_groups.register(r'', GroupViewSet, 'Group')

router_permissions = routers.DefaultRouter()
router_permissions.register(r'', PermissionViewSet, 'Permission')


url_login_patterns = [
    url(r'^$', views.AccountJWTUserAuthView.as_view(), name='login'),
    url(r'social/jwt_user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialJWTUserAuthView.as_view(),
        name='login_social_jwt_user'),
]
url_user_patterns = [
    url(r'^', include(router_users.urls), name='Restful API User'),
    url(r'^user-info', user_info, name='get_user_info'),
]
url_group_patterns = [
    url(r'^', include(router_groups.urls), name='Restful API Group'),
    url(r'^list', list_groups, name='get_list_groups'),
]
url_permission_patterns = [
    url(r'^', include(router_permissions.urls), name='List view permission'),
    url(r'^model-permissions', model_permissions, name='get_model_permissions'),
]
