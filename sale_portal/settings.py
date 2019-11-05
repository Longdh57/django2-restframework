import os
import ast

from dotenv import find_dotenv, load_dotenv
from django.core.management.commands.runserver import Command as runserver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv(os.path.join(BASE_DIR, '.env'), override=True, verbose=True)

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

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # CORS Django

    # Module in Project
    'sale_portal.administrative_unit',
    'sale_portal.cronjob',
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
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# Media file (Images, CSV, ...)
MEDIA_URL = os.environ.get('MEDIA_URL', '/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
