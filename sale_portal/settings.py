import os
import ast
import logging
import datetime

from dotenv import find_dotenv, load_dotenv
from django.core.management.commands.runserver import Command as runserver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv(os.path.join(BASE_DIR, '.env'), override=True, verbose=True)

# Logging, default at system.log, read more in https://cuccode.com/python_logging.html
logging.basicConfig(filename=os.environ.get('LOGGING_FILE', 'system.log'), level=logging.DEBUG,
                    format='[%(asctime)s] - [%(levelname)s] - %(message)s')

runserver.default_port = "9001"
print('START SALE PORTAL BACKEND...')


def get_list(text):
    return [item.strip() for item in text.split(',')]


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError(
                '{} is an invalid value for {}'.format(value, name)) from e
    return default_value


SECRET_KEY = os.environ.get('SECRET_KEY', '')

DEBUG = get_bool_from_env('DEBUG', True)

ALLOWED_HOSTS = get_list(
    os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1'), )

SALE_PORTAL_PROJECT = 'BACKEND'

# SITE URL
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:9002')

# SITE ENVIRONMENT
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'LOCAL')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # CORS Django

    # Rest framework
    'rest_framework',
    'rest_framework_datatables',

    # Module in Project
    'sale_portal.administrative_unit',
    'sale_portal.cronjob',
    'sale_portal.merchant',
    'sale_portal.qr_status',
    'sale_portal.sale_report_form',
    'sale_portal.shop',
    'sale_portal.shop_cube',
    'sale_portal.staff',
    'sale_portal.team',
    'sale_portal.terminal',
    'sale_portal.user'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS Django
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sale_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sale_portal.wsgi.wsgi_be.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'sp'),
        'USER': os.environ.get('DB_USER', 'sp_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'secret123'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    },
    'mms': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('MMS_DB_NAME', ''),
        'USER': os.environ.get('MMS_DB_USER', ''),
        'PASSWORD': os.environ.get('MMS_DB_PASSWORD', ''),
        'HOST': os.environ.get('MMS_DB_HOST', ''),
        'PORT': os.environ.get('MMS_DB_PORT', ''),
    },
}

# User Model
AUTH_USER_MODEL = 'user.User'
AUTH_PASSWORD_VALIDATORS = []

# CORS Django
FRONTEND_URL = os.environ.get('FRONTEND_URL', '')
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    FRONTEND_URL
]

# Config send email
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'test@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'secret111')
EMAIL_PORT = 587
EMAIL_USER_RECEIVER = os.environ.get('EMAIL_USER_RECEIVER', 'long.daohai4894@gmail.com')

# Internationalization
LANGUAGE_CODE = 'vi'
USE_TZ = False
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_L10N = True

# Set LOGIN_REDIRECT_URL and LOGOUT_REDIRECT_URL
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Media file (Images, CSV, ...)
MEDIA_URL = os.environ.get('MEDIA_URL', '/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Yêu cầu xác thực request
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    # add to use dadatables
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 50,
}

# Set Pagination default value
PAGINATE_BY = 25

# Custom JWT Token
# Django REST framework JWT Additional Settings
JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
        'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
        'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
        'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'sale_portal.user.views.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=3),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,
}
