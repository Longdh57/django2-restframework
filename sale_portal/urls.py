from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from sale_portal.merchant.urls import urlpatterns as merchant_urls
from sale_portal.terminal.urls import urlpatterns as terminal_urls
from sale_portal.user.urls import url_login_patterns as login_url

if settings.SALE_PORTAL_PROJECT == 'BACKEND':
    api_urlpatterns = [
        url(r'^merchant/', include((merchant_urls, 'merchant'), namespace='merchant')),
        url(r'^terminal/', include((terminal_urls, 'terminal'), namespace='terminal')),
        url(r'^login/', include(login_url)),
    ]

    urlpatterns = [
        url(r'^api/', include((api_urlpatterns))),
    ]

    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns = [
        url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
        url(r'^login/', TemplateView.as_view(template_name='login/login.html'), name='login'),
        url(r'^merchant/', include((merchant_urls, 'merchant'), namespace='merchant')),
    ]
