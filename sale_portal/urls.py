from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view

from sale_portal.user.urls import url_login_patterns as login_urls

from sale_portal.administrative_unit.urls import urlpatterns as administrative_unit_urls
from sale_portal.area.urls import urlpatterns as area_urls
from sale_portal.config_kpi.urls import urlpatterns as config_kpi_urls
from sale_portal.merchant.urls import urlpatterns as merchant_urls
from sale_portal.pos365.urls import urlpatterns as pos365_urls
from sale_portal.terminal.urls import urlpatterns as terminal_urls
from sale_portal.staff.urls import urlpatterns as staff_urls
from sale_portal.sale_report_form.urls import urlpatterns as sale_report_form_urls
from sale_portal.sale_promotion_form.urls import urlpatterns as sale_promotion_form_urls
from sale_portal.team.urls import urlpatterns as team_urls
from sale_portal.shop.urls import urlpatterns as shop_urls
from sale_portal.user.urls import url_user_patterns as user_urls
from sale_portal.user.urls import url_group_patterns as group_urls
from sale_portal.user.urls import url_permission_patterns as permission_urls
from sale_portal.user.views import CSRFGeneratorView

schema_view = get_swagger_view(title='Sale_Portal API')

api_urlpatterns = [
    url(r'^login/', include(login_urls)),
    url(r'^administrative-unit/', include((administrative_unit_urls, 'administrative_unit'),
                                          namespace='administrative_unit')),
    url(r'^areas/', include((area_urls, 'area'), namespace='area')),
    url(r'^config_kpi/', include((config_kpi_urls, 'config_kpi'), namespace='config_kpi')),
    url(r'^merchants/', include((merchant_urls, 'merchant'), namespace='merchant')),
    url(r'^pos365s/', include((pos365_urls, 'pos365'), namespace='pos365')),
    url(r'^sale-report-form/', include((sale_report_form_urls, 'sale_report_form'), namespace='sale_report_form')),
    url(r'^sale-promotion-form/',
        include((sale_promotion_form_urls, 'sale_promotion_form'), namespace='sale_promotion_form')),
    url(r'^staffs/', include((staff_urls, 'staff'), namespace='staff')),
    url(r'^teams/', include((team_urls, 'team'), namespace='team')),
    url(r'^terminals/', include((terminal_urls, 'terminal'), namespace='terminal')),
    url(r'^shop/', include((shop_urls, 'shop'), namespace='shop')),
    url(r'^users/', include((user_urls, 'user'), namespace='user')),
    url(r'^groups/', include((group_urls, 'group'), namespace='group')),
    url(r'^permissions/', include((permission_urls, 'permission'), namespace='permission')),
    url(r'^generate-csrf/$', CSRFGeneratorView.as_view()),
]
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', schema_view),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'^api/', include((api_urlpatterns, 'api'), namespace='api')),

]

urlpatterns += static('/log/', document_root=settings.LOG_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
