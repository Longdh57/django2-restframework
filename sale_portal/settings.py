import os
import ast
import logging
import datetime
import logging.config

from dotenv import find_dotenv, load_dotenv
from django.core.management.commands.runserver import Command as runserver
from structlog import configure, processors, stdlib, threadlocal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv(os.path.join(BASE_DIR, '.env'), override=True, verbose=True)

# Logging, default at system.log, read more in https://cuccode.com/python_logging.html
logging.basicConfig(filename=os.environ.get('LOGGING_FILE', 'system.log'),
                    format='[%(asctime)s] - [%(levelname)s] - %(message)s')


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


if not os.path.exists('log'):
    os.makedirs('log')

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(process)s %(thread)s %(message)s',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 1,
            'filename': 'log/log.log',
            'backupCount': 15,
            'formatter': 'json',
        },
        'request': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 1,
            'filename': 'log/request.log',
            'backupCount': 15,
            'formatter': 'json',
        }
    },
    'loggers': {
        'dev': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'request': {
            'handlers': ['request'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
)

configure(
    context_class=threadlocal.wrap_dict(dict),
    logger_factory=stdlib.LoggerFactory(),
    wrapper_class=stdlib.BoundLogger,
    processors=[
        stdlib.filter_by_level,
        stdlib.add_logger_name,
        stdlib.add_log_level,
        stdlib.PositionalArgumentsFormatter(),
        processors.TimeStamper(fmt="iso"),
        processors.StackInfoRenderer(),
        processors.format_exc_info,
        stdlib.render_to_log_kwargs]
)

runserver.default_port = os.environ.get('RUNSERVER_DEFAULT_PORT', '9001')
print('START SALE PORTAL BACKEND...')

SECRET_KEY = os.environ.get('SECRET_KEY', '')

DEBUG = get_bool_from_env('DEBUG', True)

ALLOWED_HOSTS = get_list(
    os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1'), )

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
    'django.contrib.postgres',

    # Rest framework
    'rest_framework',
    'rest_framework_datatables',
    'rest_framework_swagger',

    # Social Auth
    'rest_framework.authtoken',
    'social_django',
    'rest_social_auth',
    'oauth2_provider',
    'rest_framework_social_oauth2',

    # Module in Project
    'sale_portal.administrative_unit',
    'sale_portal.area',
    'sale_portal.config_kpi',
    'sale_portal.cronjob',
    'sale_portal.merchant',
    'sale_portal.pos365',
    'sale_portal.qr_status',
    'sale_portal.sale_report_form',
    'sale_portal.sale_promotion_form',
    'sale_portal.shop',
    'sale_portal.shop_cube',
    'sale_portal.staff',
    'sale_portal.staff_care',
    'sale_portal.team',
    'sale_portal.terminal',
    'sale_portal.user',
    'sale_portal.common'
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
    'sale_portal.middleware.RequestLogMiddleware',
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

WSGI_APPLICATION = 'sale_portal.wsgi.application'

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
    'data_warehouse': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DWH_DB_NAME', ''),
        'USER': os.environ.get('DWH_DB_USER', ''),
        'PASSWORD': os.environ.get('DWH_DB_PASSWORD', ''),
        'HOST': os.environ.get('DWH_DB_HOST', ''),
        'PORT': os.environ.get('DWH_DB_PORT', ''),
    },
}

# shop_cube table name
DWH_DB_TABLE = os.environ.get('DWH_DB_TABLE', 'full_shop_cube')

# User Model
AUTH_USER_MODEL = 'user.User'
AUTH_PASSWORD_VALIDATORS = []

# CORS Django
FRONTEND_URL = os.environ.get('FRONTEND_URL', '')
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    FRONTEND_URL
]

# Google Social OAuth2
SOCIAL_AUTH_RAISE_EXCEPTIONS = True
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = ['vnpay.vn']

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'rest_framework_social_oauth2.backends.DjangoOAuth2',
    # 'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
)

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
STATIC_ROOT = os.path.join(BASE_DIR, 'backend-static')
STATIC_URL = os.environ.get('STATIC_URL', '/backend-static/')

STATICFILES_DIRS = (
    ('staff_care', os.path.join(BASE_DIR, 'sale_portal', 'static', 'staff_care')),
    ('sale_promotion_form', os.path.join(BASE_DIR, 'sale_portal', 'static', 'sale_promotion_form')),
)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder']

# Media file (Images, CSV, ...)
MEDIA_URL = os.environ.get('MEDIA_URL', '/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

FS_IMAGE_UPLOADS = os.path.join(MEDIA_ROOT, 'images/')
FS_IMAGE_URL = os.path.join(MEDIA_URL, 'images/')

FS_DOCUMENT_UPLOADS = os.path.join(MEDIA_ROOT, 'documents/')
FS_DOCUMENT_URL = os.path.join(MEDIA_URL, 'documents/')

LOG_ROOT = os.path.join(BASE_DIR, 'log')

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
        'rest_framework_datatables.filters.DatatablesFilterBackend', 'rest_framework.filters.OrderingFilter',
    ),
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'DEFAULT_PAGINATION_CLASS': 'sale_portal.utils.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 50,
    'EXCEPTION_HANDLER': 'sale_portal.utils.exception_response.custom_exception_handler',
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

    # 'JWT_RESPONSE_PAYLOAD_HANDLER':
    #     'sale_portal.user.views.jwt_response_payload_handler',

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

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT authorization'
        }
    },
    "enabled_methods": [
        'get',
        'post',
        'put',
        'delete'
    ],
}
