import os
import time
import xlsxwriter
import logging
from datetime import datetime

from django.db.models import Q
from django.conf import settings
from django.utils import formats
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from django.contrib.auth.decorators import login_required, permission_required

from sale_portal.area.models import Area
from sale_portal.merchant.models import Merchant
from sale_portal.utils.field_formatter import format_string
from sale_portal.administrative_unit.models import QrProvince
from sale_portal.merchant.serializers import MerchantSerializer
from sale_portal.qr_status.views import get_merchant_status_list
from sale_portal.utils.queryset import get_shops_viewable_queryset
from sale_portal.utils.permission import get_user_permission_classes
from sale_portal.utils.data_export import get_data_export, ExportType
from sale_portal.utils.excel_util import check_or_create_excel_folder
from sale_portal.common.standard_response import successful_response, custom_response, Code


class MerchantViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
        API get list Merchant \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - merchant_text -- text
        - area_id -- interger
        - province_id -- interger
        - status -- number in {-1,1,2,3,4,5,6}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = MerchantSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action == 'list':
            permission_classes = get_user_permission_classes('merchant.merchant_list_data', self.request)
        if self.action == 'retrieve':
            permission_classes = get_user_permission_classes('merchant.merchant_detail', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return get_queryset_merchant_list(self.request)

    def retrieve(self, request, pk):
        """
            API get detail Merchant
        """
        return detail(request, pk)


@api_view(['GET'])
@login_required
@permission_required('merchant.merchant_list_data', raise_exception=True)
def list_merchants(request):
    """
        API get list Merchant to select \n
        Parameters for this api : Có thể bỏ trống hoặc không cần gửi lên
        - code -- text
    """

    queryset = Merchant.objects.values('id', 'merchant_code', 'merchant_name', 'merchant_brand')

    if request.user.is_superuser is False:
        shops = get_shops_viewable_queryset(request.user)
        queryset = queryset.filter(pk__in=shops.values('merchant'))

    code = request.GET.get('code', None)

    if code is not None and code != '':
        queryset = queryset.filter(Q(merchant_code__icontains=code) | Q(merchant_brand__icontains=code))

    queryset = queryset.order_by('merchant_brand')[0:settings.PAGINATE_BY]

    data = [{'id': merchant['id'], 'code': merchant['merchant_code'] + ' - ' + merchant['merchant_brand']} for
            merchant in queryset]

    return successful_response(data)


@login_required
def detail(request, pk):
    # API detail
    try:
        if request.user.is_superuser is False:
            shops = get_shops_viewable_queryset(request.user)
            merchant = Merchant.objects.filter(pk=pk, pk__in=shops.values('merchant')).first()
        else:
            merchant = Merchant.objects.filter(pk=pk).first()
        if merchant is None:
            return custom_response(Code.MERCHANT_NOT_FOUND)
        staff = merchant.get_staff()
        merchant_info = merchant.merchant_info
        data = {
            'merchant_id': merchant.id,
            'merchant_code': merchant.merchant_code,
            'merchant_brand': merchant.merchant_brand,
            'merchant_name': merchant.merchant_name,
            'address': merchant.address,
            'type': merchant.get_type().full_name if merchant.get_type() else '',
            'total_shop': merchant.shops.count(),
            'total_terminal': merchant.terminals.count(),
            'merchant_info': {
                'contact_name': merchant_info.contact_name if merchant_info else 'N/A'
            },
            'staff': {
                'full_name': staff.full_name if staff is not None else '',
                'email': staff.email if staff is not None else ''
            },
            'staff_care': {
                "full_name": merchant.staff_care.full_name if merchant.staff_care.full_name else 'N/A',
                "email": merchant.staff_care.email if merchant.staff_care.email else 'N/A',
                "team": merchant.staff_care.team.name if merchant.staff_care.team else 'N/A',
            } if merchant.staff_care else {
                "full_name": 'N/A',
                "email": 'N/A',
                "team": 'N/A',
            },
            'created_date': formats.date_format(merchant.created_date,
                                                "SHORT_DATETIME_FORMAT") if merchant.created_date else '',
            'status': int(merchant.get_status()) if merchant.get_status() else None,
            'merchant_cube': merchant.get_merchant_cube(),
        }
        return successful_response(data)
    except Exception as e:
        logging.error('Get detail merchant exception: %s', e)
        return custom_response(Code.INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@login_required
def list_status(request):
    """
        API get list status of Merchant
    """
    return successful_response(get_merchant_status_list())


@api_view(['GET'])
@login_required
@permission_required('merchant.merchant_export', raise_exception=True)
def export(request):
    """
        API export data Merchant \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - merchant_text -- text
        - area_id -- interger
        - province_id -- interger
        - status -- number in {-1,1,2,3,4,5,6}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """

    file_path = render_excel(request)

    return successful_response(file_path)


@login_required
def render_excel(request=None, return_url=True):
    check_or_create_excel_folder()

    if not os.path.exists(settings.MEDIA_ROOT + '/excel/merchant'):
        os.mkdir(os.path.join(settings.MEDIA_ROOT + '/excel', 'merchant'))

    file_name = 'merchant_' + str(int(time.time())) + '.xlsx'
    workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + '/excel/merchant/' + file_name)
    worksheet = workbook.add_worksheet('DANH SÁCH MERCHANT')

    # ------------------- font style -----------------------
    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#74beff',
        'font_color': '#ffffff',
    })

    # ------------------- header -----------------------
    worksheet.write('A1', 'Merchant ID', merge_format)
    worksheet.write('B1', 'Merchant Name', merge_format)
    worksheet.write('C1', 'Merchant Brand', merge_format)
    worksheet.write('D1', 'Tỉnh thành', merge_format)
    worksheet.write('E1', 'NV ký hợp đồng', merge_format)
    worksheet.write('F1', 'NV chăm sóc', merge_format)
    worksheet.write('G1', 'Team', merge_format)
    worksheet.write('H1', 'Ngày tạo', merge_format)
    worksheet.write('I1', 'SL Ter', merge_format)
    worksheet.write('J1', 'SLGD hôm qua', merge_format)
    worksheet.write('K1', 'SLGD K1', merge_format)
    worksheet.write('L1', 'SLGD K2', merge_format)
    worksheet.write('M1', 'SLGD K3', merge_format)
    worksheet.write('N1', 'SLGD K4', merge_format)
    worksheet.write('O1', 'Tình trạng', merge_format)
    worksheet.freeze_panes(1, 0)

    terminals = get_merchant_exports(request)

    row_num = 1
    for item in terminals:
        worksheet.write(row_num, 0, item['merchant_code'] if item['merchant_code'] else '')
        worksheet.write(row_num, 1, item['merchant_name'] if item['merchant_name'] else '')
        worksheet.write(row_num, 2, item['merchant_brand'] if item['merchant_brand'] else '')
        worksheet.write(row_num, 3, item['province_name'] if item['province_name'] else '')
        worksheet.write(row_num, 4, item['email'] if item['email'] else '')
        worksheet.write(row_num, 5, item['staff_care_email'] if item['staff_care_email'] else '')
        worksheet.write(row_num, 6, item['team_code'] if item['team_code'] else '')
        worksheet.write(row_num, 7, formats.date_format(
            item['created_date'], "SHORT_DATETIME_FORMAT") if item['created_date'] else '')
        worksheet.write(row_num, 8, item['count_ter'] if item['count_ter'] else '')
        worksheet.write(row_num, 9, item['total_number_of_tran'] if item['total_number_of_tran'] else 0)
        worksheet.write(row_num, 10, item['total_k1'] if item['total_k1'] else 0)
        worksheet.write(row_num, 11, item['total_k2'] if item['total_k2'] else 0)
        worksheet.write(row_num, 12, item['total_k3'] if item['total_k3'] else 0)
        worksheet.write(row_num, 13, item['total_k4'] if item['total_k4'] else 0)
        worksheet.write(row_num, 14, item['status'] if item['status'] else '')

        row_num += 1

    workbook.close()

    if return_url:
        return settings.MEDIA_URL + '/excel/merchant/' + file_name
    return settings.MEDIA_ROOT + '/excel/merchant/' + file_name


def get_merchant_exports(request):
    queryset = get_queryset_merchant_list(request)

    if len(queryset) > 10000 and request.user.is_superuser is False:
        raise APIException(detail='Số lượng bản ghi quá lớn (>10.000), không thể xuất dữ liệu.', code=400)

    if len(queryset) == 0:
        return Merchant.objects.none()

    return get_data_export(queryset, ExportType.MERCHANT)


def get_queryset_merchant_list(request):
    queryset = Merchant.objects.all()

    if request.user.is_superuser is False:
        shops = get_shops_viewable_queryset(request.user)
        queryset = queryset.filter(pk__in=shops.values('merchant'))

    merchant_text = request.query_params.get('merchant_text', None)
    area_id = request.query_params.get('area_id', None)
    province_id = request.query_params.get('province_id', None)
    status = request.query_params.get('status', None)
    from_date = request.query_params.get('from_date', None)
    to_date = request.query_params.get('to_date', None)

    if merchant_text is not None and merchant_text != '':
        merchant_text = format_string(merchant_text)
        queryset = queryset.filter(
            Q(merchant_code__icontains=merchant_text) | Q(merchant_name__icontains=merchant_text) | Q(
                merchant_brand__icontains=merchant_text))
    if area_id is not None and area_id != '':
        if area_id.isdigit():
            province_codes = []
            area = Area.objects.get(pk=int(area_id))
            provinces = area.get_provinces()
            for item in provinces:
                province_codes.append(item.province_code)
            queryset = queryset.filter(province_code__in=province_codes)
    if province_id is not None and province_id != '':
        if province_id.isdigit():
            province = QrProvince.objects.get(pk=int(province_id))
            queryset = queryset.filter(province_code=province.province_code)
    if status is not None and status != '':
        queryset = queryset.filter(status=status)
    if from_date is not None and from_date != '':
        queryset = queryset.filter(
            created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
    if to_date is not None and to_date != '':
        queryset = queryset.filter(
            created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

    return queryset

