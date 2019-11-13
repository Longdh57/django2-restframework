from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

url_login_patterns = [
    url(r'^', obtain_jwt_token, name='login'),
]
