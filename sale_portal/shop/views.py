import os
import ast
import json
import time
import logging
import itertools
import xlsxwriter

from unidecode import unidecode
from django.conf import settings
from django.utils import formats
from django.db import connection
from django.db.models import F, Q
from datetime import datetime, date
from rest_framework import viewsets, mixins
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.utils.html import conditional_escape
from rest_framework.exceptions import APIException
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.contrib.auth.decorators import login_required, permission_required

from sale_portal.team import TeamType
from sale_portal.area.models import Area
from sale_portal.staff.models import Staff
from sale_portal.merchant.models import Merchant
from sale_portal.terminal.models import Terminal
from sale_portal.staff_care import StaffCareType
from sale_portal.shop_cube.models import ShopCube
from sale_portal.staff_care.models import StaffCare
from sale_portal.utils.geo_utils import findDistance
from sale_portal.utils.field_formatter import format_string
from sale_portal.shop.models import Shop, ShopFullData, ShopLog
from sale_portal.utils.permission import get_user_permission_classes
from sale_portal.utils.excel_util import check_or_create_excel_folder
from sale_portal.utils.data_export import get_data_export, ExportType
from sale_portal.shop.serializers import ShopFullDataSerializer, ShopLogSerializer
from sale_portal.administrative_unit.models import QrWards, QrProvince, QrDistrict
from sale_portal.common.standard_response import successful_response, custom_response, Code
from sale_portal.utils.queryset import get_shops_viewable_queryset, get_provinces_viewable_queryset, \
    get_staffs_viewable_queryset


@api_view(['GET'])
@login_required
@permission_required('shop.shop_list_data', raise_exception=True)
def list_shop_for_search(request):
    """
        API để search full text search không dấu  các shop dựa trên địa chỉ, shop_code hoặc merchant brand, param là name
    """
    name = request.GET.get('name', None)
    user_info = request.user
    queryset = get_shops_viewable_queryset(user_info)
    if name is not None and name != '':
        name = format_string(name)
        querysetABS = queryset.filter(
            Q(code__icontains=name) | Q(merchant__merchant_brand__icontains=name) | Q(address__icontains=name)
        )[:10]
        lengQuerysetABS = len(querysetABS)

        if lengQuerysetABS < 10:
            name_en = unidecode(name).lower()
            search_query = SearchQuery(name_en)
            querysetFTS = queryset.annotate(
                rank=SearchRank(F('document'), search_query)
            ).order_by(
                '-rank'
            ).exclude(pk__in=querysetABS)[:(10 - lengQuerysetABS)]
        else:
            querysetFTS = []

    else:
        querysetABS = queryset[:10]
        querysetFTS = []

    data = []
    for shop in itertools.chain(querysetABS, querysetFTS):
        code = shop.code if shop.code is not None else 'N/A'
        address = shop.address if shop.address is not None else 'N/A'
        merchant_brand = shop.merchant.merchant_brand if shop.merchant.merchant_brand is not None else 'N/A'
        data.append({'id': shop.id, 'shop_info': code + ' - ' + merchant_brand + ' - ' + address})

    return successful_response(data)


@api_view(['GET'])
@login_required
@permission_required('shop.shop_list_data', raise_exception=True)
def list_recommend_shops(request, pk):
    '''
    API for get shop number_transaction and nearly shops \n
    :param shop_id
    '''
    all_shop = get_shops_viewable_queryset(request.user)
    current_shop = get_object_or_404(Shop, pk=pk)
    current_shop_shop_cube = ShopCube.objects.filter(shop_id=pk).first()
    day = date.today().day
    if current_shop_shop_cube is not None:
        if 1 <= day <= 7:
            current_shop_number_of_tran = current_shop_shop_cube.number_of_tran_w_1_7 \
                if current_shop_shop_cube.number_of_tran_w_1_7 is not None \
                   and current_shop_shop_cube.number_of_tran_w_1_7 != '' \
                else 'N/A'
        if 8 <= day <= 14:
            current_shop_number_of_tran = current_shop_shop_cube.number_of_tran_w_8_14 \
                if current_shop_shop_cube.number_of_tran_w_8_14 is not None \
                   and current_shop_shop_cube.number_of_tran_w_8_14 != '' \
                else 'N/A'
        if 15 <= day <= 21:
            current_shop_number_of_tran = current_shop_shop_cube.number_of_tran_w_15_21 \
                if current_shop_shop_cube.number_of_tran_w_15_21 is not None \
                   and current_shop_shop_cube.number_of_tran_w_15_21 != '' \
                else 'N/A'
        if 22 <= day:
            current_shop_number_of_tran = current_shop_shop_cube.number_of_tran_w_22_end \
                if current_shop_shop_cube.number_of_tran_w_22_end is not None \
                   and current_shop_shop_cube.number_of_tran_w_22_end != '' \
                else 'N/A'
    else:
        current_shop_number_of_tran = 'N/A'

    nearly_shops_by_latlong = []
    if current_shop.wards != '' and current_shop.wards is not None:
        try:
            shop_list = all_shop.filter(wards=current_shop.wards, activated=1).exclude(pk=pk)
            for shop in shop_list:
                code = shop.code if shop.code is not None else 'N/A'
                address = shop.address if shop.address is not None else 'N/A'
                merchant_brand = shop.merchant.merchant_brand if shop.merchant.merchant_brand is not None else 'N/A'
                if shop.latitude and shop.longitude and current_shop.latitude and current_shop.longitude:
                    distance = findDistance(shop.latitude, shop.longitude, current_shop.latitude,
                                            current_shop.longitude)
                    nearly_shops_by_latlong.append({
                        'id': shop.id,
                        'shop_info': code + ' - ' + address + ' - ' + merchant_brand,
                        'address': shop.address,
                        'latitude': shop.latitude,
                        'longitude': shop.longitude,
                        'distance_value': distance.get('value') if distance is not None else None,
                        'distance_text': distance.get('text') if distance is not None else None
                    })
            nearly_shops_by_latlong_sorted = sorted(nearly_shops_by_latlong, key=lambda k: k['distance_value'])
        except Exception as e:
            print(str(e))

    data = {
        'address': current_shop.address if current_shop.address != '' and current_shop.address is not None else '',
        'street': current_shop.street if current_shop.street != '' and current_shop.street is not None else '',
        'number_of_tran': current_shop_number_of_tran,
        'latitude': current_shop.latitude,
        'longitude': current_shop.longitude,
        'nearly_shops': nearly_shops_by_latlong_sorted
    }
    return successful_response(data)


@api_view(['GET'])
@login_required
@permission_required('shop.dashboard_shop_count', raise_exception=True)
def get_count_shop_30_days_before(request):
    shop_count = Shop.objects.filter(activated=1).count()
    with connection.cursor() as cursor:
        cursor.execute('''
            select count(*), date(created_date)
            from shop
            where created_date > current_date - interval '30 days'
            group by date(created_date)
            order by date(created_date) asc
        ''')
        columns = [col[0] for col in cursor.description]
        data_cursor = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    data_date = []
    data_value = []
    today = 0
    for item in data_cursor:
        if str(item['date']) == str(date.today().strftime("%Y-%m-%d")):
            today = item['count']
            continue
        data_date.append(str(item['date'].strftime("%d/%m/%Y")))
        data_value.append(item['count'])

    return successful_response({
        'data': {
            'data_date': data_date,
            'data_value': data_value
        },
        'today': today,
        'shop_count': shop_count
    })


class ShopViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list Shop \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
        - merchant_id -- number
        - team_id -- number
        - staff_id -- number
        - area_id -- number
        - province_id -- number
        - district_id -- number
        - ward_id -- number
        - status -- number in {0, 1, 2, 3, 4, 5, 6} = {Shop không có thông tin đường phố, Shop đã hủy or không có Terminal, Shop chưa được gán Sale, Shop phát sinh 1 GD kỳ này, Shop phát sinh 2 GD kỳ này, Shop phát sinh trên 3 GD kỳ này, Shop không phát sinh GD}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = ShopFullDataSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action == 'list':
            permission_classes = get_user_permission_classes('shop.shop_list_data', self.request)
        if self.action == 'retrieve':
            permission_classes = get_user_permission_classes('shop.shop_detail', self.request)
        if self.action == 'create':
            permission_classes = get_user_permission_classes('shop.shop_create', self.request)
        if self.action == 'update':
            permission_classes = get_user_permission_classes('shop.shop_edit', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return get_queryset_shop_list(self.request)

    def retrieve(self, request, pk):
        """
            API get detail Shop
        """
        if request.user.is_superuser is False:
            if request.user.is_area_manager or request.user.is_sale_admin:
                provinces = get_provinces_viewable_queryset(request.user)
                shop = Shop.objects.filter(pk=pk, province__in=provinces).first()
            else:
                shops = get_shops_viewable_queryset(request.user)
                shop = Shop.objects.filter(pk=pk, pk__in=shops).first()
        else:
            shop = Shop.objects.filter(pk=pk).first()

        if shop is None:
            return custom_response(Code.SHOP_NOT_FOUND)

        first_terminal = shop.terminals.order_by('created_date').first()

        if shop.shop_cube and shop.shop_cube.voucher_code_list is not None and shop.shop_cube.voucher_code_list != '[]':
            if '[' not in shop.shop_cube.voucher_code_list:
                voucher_code_list = shop.shop_cube.voucher_code_list
            else:
                voucher_code_list = ast.literal_eval(shop.shop_cube.voucher_code_list)
        else:
            voucher_code_list = ''

        data = {
            'name': shop.name,
            'code': shop.code,
            'address': shop.address,
            'street': shop.street,
            'phone': first_terminal.qr_terminal_contact.terminal_phone if (
                    first_terminal and first_terminal.qr_terminal_contact) else None,
            'created_date': formats.date_format(shop.created_date,
                                                "SHORT_DATETIME_FORMAT") if shop.created_date else '',
            'first_terminal_created_date': formats.date_format(
                first_terminal.created_date,
                "SHORT_DATETIME_FORMAT") if first_terminal and first_terminal.created_date else None,
            'merchant': {
                'id': shop.merchant.id if shop.merchant else None,
                'merchant_code': shop.merchant.merchant_code if shop.merchant else None,
                'merchant_name': shop.merchant.merchant_name if shop.merchant else None,
                'merchant_brand': shop.merchant.merchant_brand if shop.merchant else None
            },
            'staff': {
                'id': shop.staff.id if shop.staff else None,
                'full_name': shop.staff.full_name if shop.staff else None,
                'email': shop.staff.email if shop.staff else None,
                'phone': shop.staff.mobile if shop.staff else None,
            },
            'team': {
                'id': shop.team.id if shop.team else None,
                'name': shop.team.name if shop.team else None,
                'code': shop.team.code if shop.team else None
            },
            'staff_of_chain': {
                'id': shop.staff_of_chain.id if shop.staff_of_chain else None,
                'full_name': shop.staff_of_chain.full_name if shop.staff_of_chain else None,
                'email': shop.staff_of_chain.email if shop.staff_of_chain else None,
                'phone': shop.staff_of_chain.mobile if shop.staff_of_chain else None,
            },
            'team_of_chain': {
                'id': shop.team_of_chain.id if shop.team_of_chain else None,
                'name': shop.team_of_chain.name if shop.team_of_chain else None,
                'code': shop.team_of_chain.code if shop.team_of_chain else None
            },
            'shop_cube': {
                'report_date': shop.shop_cube.report_date,
                'number_of_tran': shop.shop_cube.number_of_tran,
                'number_of_tran_w_1_7': shop.shop_cube.number_of_tran_w_1_7,
                'number_of_tran_w_8_14': shop.shop_cube.number_of_tran_w_8_14,
                'number_of_tran_w_15_21': shop.shop_cube.number_of_tran_w_15_21,
                'number_of_tran_w_22_end': shop.shop_cube.number_of_tran_w_22_end,
                'voucher_code_list': voucher_code_list,
            } if shop.shop_cube else None,
            'province': {'id': shop.province.id,
                         'name': shop.province.province_name,
                         'code': shop.province.province_code} if shop.province else None,
            'district': {'id': shop.district.id,
                         'name': shop.district.district_name,
                         'code': shop.district.district_code} if shop.district else None,
            'wards': {'id': shop.wards.id,
                      'name': shop.wards.wards_name,
                      'code': shop.wards.wards_code} if shop.wards else None,
        }

        return successful_response(data)

    def update(self, request, pk):
        """
            API update Shop \n
            Request body for this api : Không được bỏ trống \n
                {
                    "name": "shop name" -- text,
                    "street": "Hoàng Cầu" -- text,
                    "address": "36 Hoàng Cầu, Đống Đa, Hà Nội" -- text,
                    "province_id": 57 -- number,
                    "district_id": 612 -- number,
                    "ward_id": 9464 -- number,
                    "description": "description" -- text,
                    "staff_id": 1016 -- number -- có thể để trống,

                }
        """
        try:
            shop = Shop.objects.filter(pk=pk).first()
            if shop is None:
                return custom_response(Code.SHOP_NOT_FOUND)
            body = json.loads(request.body)

            name = body.get('name')
            street = body.get('street')
            address = body.get('address')
            province_id = body.get('province_id')
            district_id = body.get('district_id')
            ward_id = body.get('ward_id')
            description = body.get('description')
            staff_id = body.get('staff_id')

            if name is None or name == '':
                return custom_response(Code.INVALID_BODY, 'name Invalid')

            if province_id is None or province_id == '' or not isinstance(province_id, int):
                return custom_response(Code.INVALID_BODY, 'province_id Invalid')
            if district_id is None or district_id == '' or not isinstance(district_id, int):
                return custom_response(Code.INVALID_BODY, 'district_id Invalid')
            if ward_id is None or ward_id == '' or not isinstance(ward_id, int):
                return custom_response(Code.INVALID_BODY, 'ward_id Invalid')

            ward = QrWards.objects.get(pk=ward_id)
            if ward.get_district() is None or ward.get_province() is None:
                return custom_response(Code.INVALID_BODY, 'can not find district or province from ward')
            if ward.get_district().id != district_id or ward.get_province().id != province_id:
                return custom_response(Code.INVALID_BODY, 'ward, district or province do not mapping')

            if not isinstance(staff_id, int) or staff_id is None or staff_id == '':
                if shop.staff is not None:
                    shop.staff_delete(request=request)
            else:
                staff = Staff.objects.get(pk=staff_id)
                if staff is None:
                    return custom_response(Code.INVALID_BODY, 'staff_id Invalid')
                if shop.staff != staff:
                    if shop.staff is not None:
                        shop.staff_delete(request=request)
                    shop.staff_create(staff_id=staff_id, request=request)

            shop.name = name
            shop.street = street
            shop.address = address
            shop.province_id = province_id
            shop.district_id = district_id
            shop.ward_id = ward_id
            shop.description = description
            shop.save()

            return successful_response()

        except Exception as e:
            logging.error('Update shop exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def create(self, request):
        assign_terminal_id = request.POST.get('assign_terminal_id', None)
        merchant_id = request.POST.get('merchant_id', None)
        team_id = request.POST.get('team_id', None)
        staff_id = request.POST.get('staff_id', None)
        name = request.POST.get('name', None)
        address = request.POST.get('address', None)
        province_id = request.POST.get('province_id', None)
        district_id = request.POST.get('district_id', None)
        wards_id = request.POST.get('wards_id', None)
        street = request.POST.get('street', None)
        description = request.POST.get('description', None)

        province = QrProvince.objects.filter(id=province_id).first()
        district = QrDistrict.objects.filter(id=district_id).first()
        wards = QrWards.objects.filter(id=wards_id).first()
        merchant = Merchant.objects.filter(id=merchant_id).first()
        staff = Staff.objects.filter(id=staff_id).first()

        code = Shop.objects.all().order_by("-id")[0].id + 1

        shop = Shop(
            merchant=merchant,
            name=conditional_escape(name),
            code=conditional_escape(code),
            address=conditional_escape(address),
            province=province,
            district=district,
            wards=wards,
            street=conditional_escape(street),
            description=conditional_escape(description),
            created_by=request.user
        )
        shop.save()

        if staff is not None:
            shop.staff_create(staff.id)

        if int(assign_terminal_id) != 0:
            terminal = Terminal.objects.get(pk=assign_terminal_id)
            if terminal is None:
                return custom_response('404.006')
            if shop.merchant == terminal.merchant:
                terminal.shop = shop
                terminal.save()
            else:
                return custom_response('400', 'Merchant is invalid')
        return successful_response('created')


@api_view(['GET'])
@login_required
@permission_required('shop.shop_export', raise_exception=True)
def export(request):
    """
        API export data Shop \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
        - merchant_id -- number
        - team_id -- number
        - staff_id -- number
        - area_id -- number
        - province_id -- number
        - district_id -- number
        - ward_id -- number
        - status -- number in {0, 1, 2, 3, 4, 5, 6} = {Shop không có thông tin đường phố, Shop đã hủy or không có Terminal, Shop chưa được gán Sale, Shop phát sinh 1 GD kỳ này, Shop phát sinh 2 GD kỳ này, Shop phát sinh trên 3 GD kỳ này, Shop không phát sinh GD}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """

    file_path = render_excel(request)

    return successful_response(file_path)


@login_required
def render_excel(request=None, return_url=True):
    check_or_create_excel_folder()

    if not os.path.exists(settings.MEDIA_ROOT + '/excel/shop'):
        os.mkdir(os.path.join(settings.MEDIA_ROOT + '/excel', 'shop'))

    file_name = 'shop_' + str(int(time.time())) + '.xlsx'
    workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + '/excel/shop/' + file_name)
    worksheet = workbook.add_worksheet('DANH SÁCH SHOP')

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
    worksheet.write('A1', 'Shop ID', merge_format)
    worksheet.write('B1', 'MID', merge_format)
    worksheet.write('C1', 'Merchant Brand', merge_format)
    worksheet.write('D1', 'Merchant Name', merge_format)
    worksheet.write('E1', 'Nhóm ngành', merge_format)
    worksheet.write('F1', 'Mã CTKM', merge_format)
    worksheet.write('G1', 'Sale', merge_format)
    worksheet.write('H1', 'Team', merge_format)
    worksheet.write('I1', 'Tỉnh/Thành phố', merge_format)
    worksheet.write('J1', 'Quận/Huyện', merge_format)
    worksheet.write('K1', 'Phường/Xã', merge_format)
    worksheet.write('L1', 'Địa chỉ', merge_format)
    worksheet.write('M1', 'Số lượng Ter', merge_format)
    worksheet.write('N1', 'SLGD tuần 1 (1-7)', merge_format)
    worksheet.write('O1', 'SLGD tuần 2 (8-14)', merge_format)
    worksheet.write('P1', 'SLGD tuần 3 (15-21)', merge_format)
    worksheet.write('Q1', 'SLGD tuần 4 (22-hết tháng)', merge_format)
    worksheet.write('R1', 'Ngày tạo', merge_format)
    worksheet.freeze_panes(1, 0)

    shops = get_shop_exports(request)

    row_num = 1
    for item in shops:
        worksheet.write(row_num, 0, item['id'])
        worksheet.write(row_num, 1, item['merchant_code'] if item['merchant_code'] else '')
        worksheet.write(row_num, 2, item['merchant_brand'] if item['merchant_brand'] else '')
        worksheet.write(row_num, 3, item['merchant_name'] if item['merchant_code'] else '')
        worksheet.write(row_num, 4, item['department'] if item['department'] else '')
        worksheet.write(row_num, 5, item['ctkm'] if item['ctkm'] else '')
        worksheet.write(row_num, 6, item['staff_email'] if item['staff_email'] else '')
        worksheet.write(row_num, 7, item['team_code'] if item['team_code'] else '')
        worksheet.write(row_num, 8, item['province_name'] if item['province_name'] else '')
        worksheet.write(row_num, 9, item['district_name'] if item['district_name'] else '')
        worksheet.write(row_num, 10, item['wards_name'] if item['wards_name'] else '')
        worksheet.write(row_num, 11, item['address'] if item['address'] else '')
        worksheet.write(row_num, 12, item['count_ter'] if item['count_ter'] else 0)
        worksheet.write(row_num, 13, item['k1'] if item['k1'] else 0)
        worksheet.write(row_num, 14, item['k2'] if item['k2'] else 0)
        worksheet.write(row_num, 15, item['k3'] if item['k3'] else 0)
        worksheet.write(row_num, 16, item['k4'] if item['k4'] else 0)
        worksheet.write(row_num, 17, formats.date_format(item['created_date'], "SHORT_DATETIME_FORMAT") if item[
            'created_date'] else '')

        row_num += 1

    workbook.close()

    if return_url:
        return settings.MEDIA_URL + '/excel/shop/' + file_name
    return settings.MEDIA_ROOT + '/excel/shop/' + file_name


def get_shop_exports(request):
    queryset = get_queryset_shop_list(request, export_data=True)

    if len(queryset) > 15000 and request.user.is_superuser is False:
        raise APIException(detail='Số lượng bản ghi quá lớn (>15.000), không thể xuất dữ liệu.', code=400)

    if len(queryset) == 0:
        return Shop.objects.none()

    return get_data_export(queryset, ExportType.SHOP)


def get_queryset_shop_list(request, export_data=False):
    status = request.query_params.get('status', None)

    shop_obj = Shop
    if not export_data:
        shop_obj = ShopFullData

    if status is not None and status != '':
        if status == '0':
            queryset = shop_obj.objects.shop_active().filter(Q(street__isnull=True) | Q(street=''))
        elif status == '1':
            queryset = shop_obj.objects.shop_disable()
        elif status == '2':
            shop_caring_lists = StaffCare.objects.filter(type=StaffCareType.STAFF_SHOP).values('shop')
            queryset = shop_obj.objects.shop_active().filter(~Q(pk__in=shop_caring_lists))
        else:
            if status == '3':
                shop_lists = ShopCube.objects.number_of_tran_this_week(value=1).values('shop_id')
            elif status == '4':
                shop_lists = ShopCube.objects.number_of_tran_this_week(value=2).values('shop_id')
            elif status == '5':
                shop_lists = ShopCube.objects.number_of_tran_this_week(value=3).values('shop_id')
            else:
                shop_lists = ShopCube.objects.number_of_tran_this_week(value=0).values('shop_id')
            queryset = shop_obj.objects.shop_active().filter(pk__in=shop_lists)
    else:
        queryset = shop_obj.objects.shop_active()

    if request.user.is_superuser is False:
        if request.user.is_area_manager or request.user.is_sale_admin:
            if request.user.is_manager_outside_vnpay:
                shops = get_shops_viewable_queryset(request.user)
                queryset = queryset.filter(pk__in=shops)
            else:
                provinces_viewable = get_provinces_viewable_queryset(request.user)
                cross_assign_status = request.query_params.get('cross_assign_status', None)
                if cross_assign_status is not None and cross_assign_status != '':
                    if cross_assign_status == '0':
                        staff_viewable = get_staffs_viewable_queryset(request.user)
                        shop_ids = StaffCare.objects.filter(staff__in=staff_viewable, type=StaffCareType.STAFF_SHOP) \
                            .values('shop_id')
                        queryset = queryset.filter(pk__in=shop_ids).exclude(province__in=provinces_viewable)
                    if cross_assign_status == '1':
                        staff_viewable = get_staffs_viewable_queryset(request.user)
                        shop_ids = StaffCare.objects.filter(type=StaffCareType.STAFF_SHOP) \
                            .exclude(staff__in=staff_viewable).values('shop_id')
                        queryset = queryset.filter(pk__in=shop_ids, province__in=provinces_viewable)
                    if cross_assign_status == '2':
                        staff_viewable = get_staffs_viewable_queryset(request.user)
                        shop_id_can_view = StaffCare.objects.filter(staff__in=staff_viewable, type=StaffCareType.STAFF_SHOP) \
                            .values('shop_id')
                        shop_id_can_not_view = StaffCare.objects.filter(type=StaffCareType.STAFF_SHOP) \
                            .exclude(staff__in=staff_viewable).values('shop_id')
                        queryset = queryset.filter(
                            (Q(pk__in=shop_id_can_not_view) & Q(province__in=provinces_viewable)) |
                            (Q(pk__in=shop_id_can_view) & ~Q(province__in=provinces_viewable))
                        )
                else:
                    queryset = queryset.filter(province__in=provinces_viewable)
        else:
            shops = get_shops_viewable_queryset(request.user)
            queryset = queryset.filter(pk__in=shops)

    code = request.query_params.get('code', None)
    merchant_id = request.query_params.get('merchant_id', None)
    team_id = request.query_params.get('team_id', None)
    staff_id = request.query_params.get('staff_id', None)
    area_id = request.query_params.get('area_id', None)
    province_id = request.query_params.get('province_id', None)
    district_id = request.query_params.get('district_id', None)
    ward_id = request.query_params.get('ward_id', None)
    from_date = request.query_params.get('from_date', None)
    to_date = request.query_params.get('to_date', None)

    if code is not None and code != '':
        code = format_string(code)
        queryset = queryset.filter(Q(code__icontains=code) | Q(name__icontains=code))

    if merchant_id is not None and merchant_id != '':
        queryset = queryset.filter(merchant_id=merchant_id)

    if team_id is not None and team_id != '':
        staffs = Staff.objects.filter(team=team_id)
        shop_ids = StaffCare.objects.filter(staff__in=staffs, type=StaffCareType.STAFF_SHOP).values('shop_id')
        queryset = queryset.filter(pk__in=shop_ids)

    if staff_id is not None and staff_id != '':
        shop_ids = StaffCare.objects.filter(staff=staff_id, type=StaffCareType.STAFF_SHOP).values('shop_id')
        queryset = queryset.filter(pk__in=shop_ids)

    if area_id is not None and area_id != '':
        if area_id.isdigit():
            area = Area.objects.get(pk=int(area_id))
            provinces = area.get_provinces()
            queryset = queryset.filter(province_id__in=provinces)

    if province_id is not None and province_id != '':
        queryset = queryset.filter(province_id=province_id)

    if district_id is not None and district_id != '':
        queryset = queryset.filter(district_id=district_id)

    if ward_id is not None and ward_id != '':
        queryset = queryset.filter(wards_id=ward_id)

    if from_date is not None and from_date != '':
        queryset = queryset.filter(
            created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))

    if to_date is not None and to_date != '':
        queryset = queryset.filter(
            created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))
    return queryset


@api_view(['POST'])
@login_required
@permission_required('shop.shop_create_from_ter', raise_exception=True)
def create_from_terminal(request):
    if request.method == 'POST':
        terminal_id = request.POST.get('terminal_id', None)
        address = request.POST.get('address', None)
        street = request.POST.get('street', None)
        auto_create = request.POST.get('auto_create', None)

        terminal = Terminal.objects.get(pk=int(terminal_id))

    elif request.method == 'OTHER':
        terminal = request.terminal
        address = request.address
        street = request.street

    else:
        return custom_response(Code.NOT_IMPLEMENTED)

    staff = None
    staff_of_chain = None
    merchant = terminal.merchant
    if merchant is not None:
        staff = merchant.get_staff()
        if staff is not None:
            team = staff.team
            if team is not None and team.type != TeamType.TEAM_SALE:
                staff_of_chain = merchant.get_staff()

    shop = Shop(
        merchant=terminal.merchant,
        name=conditional_escape(terminal.terminal_name),
        address=conditional_escape(address),
        province_id=terminal.get_province().id if (terminal.get_province() is not None) else None,
        district_id=terminal.get_district().id if (terminal.get_district() is not None) else None,
        wards_id=terminal.get_wards().id if (terminal.get_wards() is not None) else None,
        street=conditional_escape(street),
        created_by=request.user
    )
    shop.save()

    terminal.shop = shop
    terminal.save()

    if staff is not None:
        shop.staff_create(staff.id)

    if staff_of_chain is not None:
        shop.staff_of_chain_create(staff.id)

    if request.method == 'OTHER':
        return True

    data = {
        'shop_id': shop.pk
    }
    return successful_response(data)


@api_view(['POST'])
@login_required
@permission_required('shop.shop_assign', raise_exception=True)
def assign_ter_to_shop(request):
    ter_id = request.POST.get('ter_id')
    shop_id = request.POST.get('shop_id')
    terminal = get_object_or_404(Terminal, pk=ter_id)
    shop = get_object_or_404(Shop, pk=shop_id)

    if shop.merchant != terminal.merchant:
        return custom_response(Code.DATA_ERROR, "Shop và terminal không cùng merchant")
    else:
        terminal.shop = shop
        terminal.save()
    return successful_response({'id': shop.id})


class ShopLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ShopLogSerializer

    def get_queryset(self):
        return get_queryset_shop_log_list(self.request)


def get_queryset_shop_log_list(request):
    queryset = ShopLog.objects.order_by('-id').all()

    shop_id = request.query_params.get('shop_id', None)

    if shop_id is not None and shop_id != '':
        queryset = queryset.filter(shop_id=shop_id)

    return queryset
