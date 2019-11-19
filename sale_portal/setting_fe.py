import os
import ast

from dotenv import find_dotenv, load_dotenv
from django.core.management.commands.runserver import Command as runserver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv(os.path.join(BASE_DIR, '.env'), override=True, verbose=True)

runserver.default_port = "9002"
print('START SALE PORTAL FRONTEND...')


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

SALE_PORTAL_PROJECT = 'FRONTEND'

# SITE URL
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:9002')

# API URL
API_URL = os.environ.get('API_URL', 'localhost:9001')

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

    # Rest framework
    'rest_framework',

    # Module in Project
    'sale_portal.administrative_unit',
    'sale_portal.cronjob',
    'sale_portal.merchant',
    'sale_portal.qr_status',
    'sale_portal.shop',
    'sale_portal.shop_cube',
    'sale_portal.staff',
    'sale_portal.team',
    'sale_portal.temp',
    'sale_portal.terminal',
    'sale_portal.user',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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

WSGI_APPLICATION = 'sale_portal.wsgi.wsgi_fe.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# CORS Django
FRONTEND_URL = os.environ.get('FRONTEND_URL', '')


# Internationalization
LANGUAGE_CODE = 'vi'
USE_TZ = False
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_L10N = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = os.environ.get('STATIC_URL', '/static/')

STATICFILES_DIRS = (
    ('assets', os.path.join(BASE_DIR, 'sale_portal', 'static', 'assets')),
    ('global_assets', os.path.join(BASE_DIR, 'sale_portal', 'static', 'global_assets')),
)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder']

# User Model
AUTH_USER_MODEL = 'user.User'
AUTH_PASSWORD_VALIDATORS = []
