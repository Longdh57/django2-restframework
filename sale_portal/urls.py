from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view

from sale_portal.user.urls import url_login_patterns as login_urls
from sale_portal.user.urls import url_account_patterns as account_urls
from sale_portal.merchant.urls import urlpatterns as merchant_urls
from sale_portal.terminal.urls import urlpatterns as terminal_urls
from sale_portal.staff.urls import urlpatterns as staff_urls
from sale_portal.sale_report_form.urls import urlpatterns as sale_report_form_urls
from sale_portal.sale_promotion_form.urls import urlpatterns as sale_promotion_form_urls
from sale_portal.team.urls import urlpatterns as team_urls
from sale_portal.shop.urls import urlpatterns as shop_urls

schema_view = get_swagger_view(title='Sale_Portal API')

api_urlpatterns = [
    url(r'^login', include(login_urls)),
    url(r'^users/', include((account_urls, 'account'), namespace='account')),
    url(r'^merchants/', include((merchant_urls, 'merchant'), namespace='merchant')),
    url(r'^sale-report-form/', include((sale_report_form_urls, 'sale_report_form'), namespace='sale_report_form')),
    url(r'^sale-promotion-form/', include((sale_promotion_form_urls, 'sale_promotion_form'), namespace='sale_promotion_form')),
    url(r'^staffs/', include((staff_urls, 'staff'), namespace='staff')),
    url(r'^teams/', include((team_urls, 'team'), namespace='team')),
    url(r'^terminals/', include((terminal_urls, 'terminal'), namespace='terminal')),
    url(r'^shop/', include((shop_urls, 'shop'), namespace='shop')),
]

urlpatterns = [
    url(r'^$', schema_view),
    url(r'^api/', include((api_urlpatterns, 'api'), namespace='api')),
]

urlpatterns += static('/log/', document_root=settings.LOG_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
