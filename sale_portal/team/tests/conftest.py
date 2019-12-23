import os
import pytest

from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('TEST_DB_NAME', 'sp_pytest'),
        'USER': os.environ.get('TEST_DB_USER', 'sp_user'),
        'PASSWORD': os.environ.get('TEST_DB_PASSWORD', 'secret123'),
        'HOST': os.environ.get('TEST_DB_HOST', 'localhost'),
        'PORT': os.environ.get('TEST_DB_PORT', '5432'),
    }
