from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from .views import create_account_group

url_login_patterns = [
    url(r'^', obtain_jwt_token, name='login'),
]
url_account_patterns = [
    url(r'^group', create_account_group, name='create_account_group'),
]
