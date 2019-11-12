from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from .views import test_api

url_login_patterns = [
    url(r'^', obtain_jwt_token, name='login'),
]

url_test_patterns = [
    url(r'^', test_api, name='test_api'),
]
