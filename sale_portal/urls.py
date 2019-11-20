from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from sale_portal.user.urls import url_login_patterns as login_urls
from sale_portal.merchant.urls import urlpatterns as merchant_urls
from sale_portal.terminal.urls import urlpatterns as terminal_urls
from sale_portal.staff.urls import urlpatterns as staff_urls
from sale_portal.team.urls import urlpatterns as team_urls
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Sale_Portal API')


if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    api_urlpatterns = [
        url(r'^login', include(login_urls)),
        url(r'^merchant/', include((merchant_urls, 'merchant'), namespace='merchant')),
        url(r'^terminal/', include((terminal_urls, 'terminal'), namespace='terminal')),
        url(r'^staff/', include((staff_urls, 'staff'), namespace='staff')),
        url(r'^team/', include((team_urls, 'team'), namespace='team')),
    ]

    urlpatterns = [
        url(r'^$', schema_view),
        url(r'^api/', include((api_urlpatterns))),
    ]

    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns = [
        url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
        url(r'^login/', TemplateView.as_view(template_name='login/login.html'), name='login'),
        url(r'^merchant/', include((merchant_urls, 'merchant'), namespace='merchant')),
        url(r'^terminal/', include((terminal_urls, 'terminal'), namespace='terminal')),
    ]
