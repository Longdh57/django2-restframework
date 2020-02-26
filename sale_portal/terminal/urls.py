from django.conf.urls import url, include
from rest_framework import routers

from .views import TerminalViewSet, list_terminals, list_status, \
    count_terminal_30_days_before, count_terminal_30_days_before_heatmap, export

router = routers.DefaultRouter()
router.register(r'', TerminalViewSet, 'Terminal')

urlpatterns = [
    url(r'^list', list_terminals, name='get_list_terminals'),
    url(r'^status', list_status, name='get_list_status'),
    url(r'^export', export, name='export_data_terminal'),
    url(r'^count-terminal-30-days-before/$', count_terminal_30_days_before,
        name='get-count-terminal-30-days-before'),
    url(r'^count-terminal-30-days-before-heatmap/$', count_terminal_30_days_before_heatmap,
        name='get-count-terminal-30-days-before-heatmap'),
    url(r'^', include(router.urls), name='Restful API Terminal'),

]
