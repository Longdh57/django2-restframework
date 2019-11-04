import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sale_portal.setting_fe')

application = get_wsgi_application()
