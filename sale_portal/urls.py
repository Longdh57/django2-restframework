from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from sale_portal.user.urls import url_login_patterns as login_urls
from sale_portal.merchant.urls import urlpatterns as merchant_urls
from sale_portal.terminal.urls import urlpatterns as terminal_urls
from sale_portal.staff.urls import urlpatterns as staff_urls
from sale_portal.sale_report_form.urls import urlpatterns as sale_report_form_urls
from sale_portal.team.urls import urlpatterns as team_urls
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Sale_Portal API')

api_urlpatterns = [
    url(r'^login', include(login_urls)),
    url(r'^merchants/', include((merchant_urls, 'merchant'), namespace='merchant')),
    url(r'^sale-report-form/', include((sale_report_form_urls, 'sale_report_form'), namespace='sale_report_form')),
    url(r'^staffs/', include((staff_urls, 'staff'), namespace='staff')),
    url(r'^teams/', include((team_urls, 'team'), namespace='team')),
    url(r'^terminals/', include((terminal_urls, 'terminal'), namespace='terminal')),
]

urlpatterns = [
    url(r'^$', schema_view),
    url(r'^api/', include((api_urlpatterns))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
