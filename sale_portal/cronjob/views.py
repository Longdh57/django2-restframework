from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.core import management
from django.http import JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view

from sale_portal.common.standard_response import successful_response
from sale_portal.cronjob.models import CronjobLog
from sale_portal.cronjob.serializers import CronjobLogSerializer
from sale_portal.administrative_unit.management.commands import repair_id_seq
from sale_portal.administrative_unit.management.commands import administrative_unit_sync
from sale_portal.merchant.management.commands import merchant_synchronize_change
from sale_portal.merchant.management.commands import qr_merchant_info_sync
from sale_portal.merchant.management.commands import qr_merchant_sync_daily
from sale_portal.merchant.management.commands import qr_type_merchant_sync
from sale_portal.qr_status.management.commands import qr_status_sync
from sale_portal.shop.management.commands import auto_create_shop_daily
from sale_portal.shop_cube.management.commands import shop_cube_sync_daily
from sale_portal.staff.management.commands import qr_staff_sync_daily
from sale_portal.staff.management.commands import staff_synchronize_change
from sale_portal.terminal.management.commands import qr_terminal_contact_sync_daily
from sale_portal.terminal.management.commands import qr_terminal_sync_daily
from sale_portal.terminal.management.commands import terminal_synchronize_change
from sale_portal.utils.permission import get_user_permission_classes

jobName = [
    'repair_id_seq', 'administrative_unit_sync',
    'merchant_synchronize_change', 'qr_merchant_info_sync',
    'qr_merchant_sync_daily', 'qr_type_merchant_sync',
    'qr_status_sync', 'auto_create_shop_daily',
    'shop_cube_sync_daily', 'qr_staff_sync_daily',
    'staff_synchronize_change', 'qr_terminal_contact_sync_daily',
    'qr_terminal_sync_daily', 'terminal_synchronize_change'
]


class CronjobLogViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
        API get list Area \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
        - province -- text
    """
    serializer_class = CronjobLogSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('cronjob_log.cronjob_list_log', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = CronjobLog.objects.all()
        date = self.request.query_params.get('date', None)

        if date is not None and date != '':
            queryset = queryset.filter(
                created_date__date=(datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')))

        return queryset


@api_view(['GET'])
@login_required
@permission_required('cronjob_log.cronjob_list_name', raise_exception=True)
def getAllJobName(request):
    data = [{"jobName": n} for n in jobName]
    return successful_response(data)


@api_view(['GET'])
@login_required
@permission_required('cronjob_log.cronjob_run_manual', raise_exception=True)
def runJobManual(request):
    job_name = request.GET.get('job_name', None)
    if job_name is None:
        return JsonResponse({
            'data': 'job_name is None',
            'status': False
        }, status=400)
    hasJob = False
    for jn in jobName:
        if jn == job_name:
            hasJob = True
            break
    if not hasJob:
        return JsonResponse({
            'data': 'job_name is not exist',
            'status': False
        }, status=400)
    try:
        # management.call_command(job_name)
        cmd = globals()[job_name].Command()
        if job_name == 'sale_portal_ingestion_sync_daily':
            management.call_command('sale_portal_ingestion_sync_daily', run_by_os=0)
        elif job_name == 'export_report_to_google_spreadsheet_daily':
            management.call_command('export_report_to_google_spreadsheet_daily', run_by_os=0)
        else:
            cmd.handle()
    except Exception as e:
        return JsonResponse({
            'data': 'server error: ' + str(e),
            'status': False
        }, status=500)
    return successful_response()


@api_view(['GET'])
@login_required
def get_job_status(request):
    data = {}
    today = datetime.now()
    today = today.strftime("%d/%m/%Y")

    auto_create_shop_daily_status = \
        CronjobLog.objects.filter(name='auto_create_shop_daily',
                                  status=1,
                                  created_date__date=(datetime.strptime(today, '%d/%m/%Y').strftime('%Y-%m-%d'))
                                  ).first()
    if auto_create_shop_daily_status is None:
        data['sync_ter'] = 'Hệ thống đang cập nhật data nhân viên, terminal, merchant mới hôm qua'

    shop_cube_sync_daily_status = \
        CronjobLog.objects.filter(name='shop_cube_sync_daily',
                                  status=1,
                                  created_date__date=(datetime.strptime(today, '%d/%m/%Y').strftime('%Y-%m-%d'))
                                  ).first()

    if shop_cube_sync_daily_status is None:
        data['sync_shop_cube'] = 'Hệ thống đang cập nhật data giao dịch và point ngày hôm qua'

    return JsonResponse({
        'data': data,
    }, status=200)
