import itertools
import os
import time
import xlsxwriter
from django.conf import settings
from datetime import datetime, date

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db import connection
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils import formats
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from unidecode import unidecode

from sale_portal.common.standard_response import successful_response, custom_response, Code
from sale_portal.shop.models import Shop
from sale_portal.shop.serializers import ShopSerializer
from sale_portal.shop_cube.models import ShopCube
from sale_portal.staff.models import Staff
from sale_portal.staff_care import StaffCareType
from sale_portal.staff_care.models import StaffCare
from sale_portal.utils.excel_util import check_or_create_excel_folder
from sale_portal.utils.field_formatter import format_string
from sale_portal.utils.geo_utils import findDistance
from sale_portal.utils.permission import get_user_permission_classes
from sale_portal.utils.queryset import get_shops_viewable_queryset, get_provinces_viewable_queryset


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
    # if not user_info.is_superuser:
    #     group = user_info.get_group()
    #     if group is None or group.status is False:
    #         return successful_response([])
    #     if group.name == ROLE_SALE_MANAGER or group.name == ROLE_SALE_ADMIN:
    #         provinces = QrProvince.objects.none()
    #         for area in user_info.area_set.all():
    #             provinces |= area.get_provinces()
    #         queryset = Shop.objects.filter(province__in=provinces)
    #     else:
    #         staff = Staff.objects.filter(email=user_info.email).first()
    #         if staff and staff.team:
    #             if staff.role == StaffTeamRoleType.TEAM_MANAGEMENT:
    #                 staffs = Staff.objects.filter(team_id=staff.team.id)
    #                 list_shop_id = [s.shop_id for s in
    #                                 StaffCare.objects.filter(staff__in=staffs, type=StaffCareType.STAFF_SHOP)]
    #                 queryset = Shop.objects.filter(pk__in=list_shop_id)
    #             else:
    #                 list_shop_id = [s.shop_id for s in StaffCare.objects.filter(staff=staff, type=StaffCareType.STAFF_SHOP)]
    #                 queryset = Shop.objects.filter(pk__in=list_shop_id)
    #         else:
    #             return successful_response([])
    # else:
    #     queryset = Shop.objects.all()

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
    current_shop = get_object_or_404(Shop, pk=pk)
    current_shop_shop_cube = ShopCube.objects.filter(shop_id=pk).first()

    if current_shop_shop_cube is not None:
        current_shop_number_of_tran = current_shop_shop_cube.number_of_tran_30d \
            if current_shop_shop_cube.number_of_tran_30d is not None \
               and current_shop_shop_cube.number_of_tran_30d != '' \
            else 'N/A'
    else:
        current_shop_number_of_tran = 'N/A'

    nearly_shops_by_latlong = []
    if current_shop.district != '' and current_shop.district is not None:
        for shop in Shop.objects.filter(district=current_shop.district).exclude(pk=pk):
            code = shop.code if shop.code is not None else 'N/A'
            address = shop.address if shop.address is not None else 'N/A'
            merchant_brand = shop.merchant.merchant_brand if shop.merchant.merchant_brand is not None else 'N/A'
            if shop.latitude and shop.longitude and current_shop.latitude and current_shop.longitude:
                distance = findDistance(shop.latitude, shop.longitude, current_shop.latitude, current_shop.longitude)
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

    data = {
        'address': current_shop.address if current_shop.address != '' and current_shop.address is not None else 'N/A',
        'street': current_shop.street if current_shop.street != '' and current_shop.street is not None else 'N/A',
        'number_of_tran': current_shop_number_of_tran,
        'latitude': current_shop.latitude,
        'longitude': current_shop.longitude,
        'nearly_shops': nearly_shops_by_latlong_sorted[:3]
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
        - province_id -- number
        - district_id -- number
        - ward_id -- number
        - status -- number in {0, 1, 2, 3, 4, 5, 6} = {Shop không có thông tin đường phố, Shop đã hủy or không có Terminal, Shop chưa được gán Sale, Shop phát sinh 1 GD kỳ này, Shop phát sinh 2 GD kỳ này, Shop phát sinh trên 3 GD kỳ này, Shop không phát sinh GD}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = ShopSerializer

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
        status = self.request.query_params.get('status', None)
        if status is not None and status != '':
            if status == '0':
                queryset = Shop.objects.shop_active().filter(Q(street__isnull=True) | Q(street=''))
            elif status == '1':
                queryset = Shop.objects.shop_disable()
            elif status == '2':
                shop_caring_lists = StaffCare.objects.filter(type=StaffCareType.STAFF_SHOP).values('shop')
                queryset = Shop.objects.shop_active().filter(~Q(pk__in=shop_caring_lists))
            else:
                if status == '3':
                    shop_lists = ShopCube.objects.number_of_tran_this_week(value=1).values('shop_id')
                elif status == '4':
                    shop_lists = ShopCube.objects.number_of_tran_this_week(value=2).values('shop_id')
                elif status == '5':
                    shop_lists = ShopCube.objects.number_of_tran_this_week(value=3).values('shop_id')
                else:
                    shop_lists = ShopCube.objects.number_of_tran_this_week(value=0).values('shop_id')
                queryset = Shop.objects.shop_active().filter(pk__in=shop_lists)
        else:
            queryset = Shop.objects.shop_active()

        if self.request.user.is_superuser is False:
            if self.request.user.is_area_manager or self.request.user.is_sale_admin:
                provinces = get_provinces_viewable_queryset(self.request.user)
                queryset = queryset.filter(province__in=provinces)
            else:
                shops = get_shops_viewable_queryset(self.request.user)
                queryset = queryset.filter(pk__in=shops)

        code = self.request.query_params.get('code', None)
        merchant_id = self.request.query_params.get('merchant_id', None)
        team_id = self.request.query_params.get('team_id', None)
        staff_id = self.request.query_params.get('staff_id', None)
        province_id = self.request.query_params.get('province_id', None)
        district_id = self.request.query_params.get('district_id', None)
        ward_id = self.request.query_params.get('ward_id', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if code is not None and code != '':
            code = format_string(code)
            queryset = queryset.filter(code__icontains=code)

        if merchant_id is not None and merchant_id != '':
            queryset = queryset.filter(merchant_id=merchant_id)

        if team_id is not None and team_id != '':
            staffs = Staff.objects.filter(team=team_id)
            shop_ids = StaffCare.objects.filter(staff__in=staffs, type=StaffCareType.STAFF_SHOP).values('shop_id')
            queryset = queryset.filter(pk__in=shop_ids)

        if staff_id is not None and staff_id != '':
            shop_ids = StaffCare.objects.filter(staff=staff_id, type=StaffCareType.STAFF_SHOP).values('shop_id')
            queryset = queryset.filter(pk__in=shop_ids)

        if province_id is not None and province_id != '':
            queryset = queryset.filter(province=province_id)

        if district_id is not None and district_id != '':
            queryset = queryset.filter(district=district_id)

        if ward_id is not None and ward_id != '':
            queryset = queryset.filter(ward=ward_id)

        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

        return queryset

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
                'merchant_code': shop.merchant.merchant_code if shop.merchant else None,
                'merchant_name': shop.merchant.merchant_name if shop.merchant else None,
                'merchant_brand': shop.merchant.merchant_brand if shop.merchant else None
            },
            'staff': {
                'full_name': shop.staff.full_name if shop.staff else None,
                'email': shop.staff.email if shop.staff else None,
                'phone': shop.staff.mobile if shop.staff else None,
            },
            'team': {
                'name': shop.team.name if shop.team else None,
                'code': shop.team.code if shop.team else None
            },
            'staff_of_chain': {
                'full_name': shop.staff_of_chain.full_name if shop.staff_of_chain else None,
                'email': shop.staff_of_chain.email if shop.staff_of_chain else None,
                'phone': shop.staff_of_chain.mobile if shop.staff_of_chain else None,
            },
            'team_of_chain': {
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
            } if shop.shop_cube else None
        }

        return successful_response(data)


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
    worksheet.write('B1', 'Merchant Brand', merge_format)
    worksheet.write('C1', 'Sale Email', merge_format)
    worksheet.write('D1', 'Team Code', merge_format)
    worksheet.write('E1', 'Tỉnh/Thành phố', merge_format)
    worksheet.write('F1', 'Quận/Huyện', merge_format)
    worksheet.write('G1', 'Phường/Xã', merge_format)
    worksheet.write('H1', 'Địa chỉ', merge_format)
    worksheet.write('I1', 'Số lượng Ter', merge_format)
    worksheet.write('J1', 'SLGD tuần 1 (1-7)', merge_format)
    worksheet.write('K1', 'SLGD tuần 2 (8-14)', merge_format)
    worksheet.write('L1', 'SLGD tuần 3 (15-21)', merge_format)
    worksheet.write('M1', 'SLGD tuần 4 (22-hết tháng)', merge_format)
    worksheet.write('N1', 'Ngày tạo', merge_format)
    worksheet.freeze_panes(1, 0)

    shop_list = get_shop_exports(request)

    row_num = 1
    for item in shop_list.all():
        shop_cube = ShopCube.objects.filter(shop_id=item.pk).order_by('-report_date').first()

        staff_id = StaffCare.objects.filter(shop=item, type=StaffCareType.STAFF_SHOP).values('staff')
        staff = Staff.objects.filter(pk=staff_id[0]['staff']).first() if staff_id else None
        worksheet.write(row_num, 0, item.id)
        worksheet.write(row_num, 1, item.merchant.merchant_brand if item.merchant else '')
        worksheet.write(row_num, 2, staff.email if staff else '')
        worksheet.write(row_num, 3, staff.team.code if staff and staff.team else '')
        worksheet.write(row_num, 4, item.province.province_name if item.province else '')
        worksheet.write(row_num, 5, item.district.district_name if item.district else '')
        worksheet.write(row_num, 6, item.wards.wards_name if item.wards else '')
        worksheet.write(row_num, 7, item.address if item.address else '')
        worksheet.write(row_num, 8, item.terminals.count())
        worksheet.write(row_num, 9, shop_cube.number_of_tran_w_1_7 if shop_cube else 0)
        worksheet.write(row_num, 10, shop_cube.number_of_tran_w_8_14 if shop_cube else 0)
        worksheet.write(row_num, 11, shop_cube.number_of_tran_w_15_21 if shop_cube else 0)
        worksheet.write(row_num, 12, shop_cube.number_of_tran_w_22_end if shop_cube else 0)
        worksheet.write(row_num, 13,
                        formats.date_format(item.created_date, "SHORT_DATETIME_FORMAT") if item.created_date else '')

        row_num += 1

    workbook.close()

    if return_url:
        return settings.MEDIA_URL + '/excel/shop/' + file_name
    return settings.MEDIA_ROOT + '/excel/shop/' + file_name


def get_shop_exports(request):
    status = request.query_params.get('status', None)
    if status is not None and status != '':
        if status == '0':
            queryset = Shop.objects.shop_active().filter(Q(street__isnull=True) | Q(street=''))
        elif status == '1':
            queryset = Shop.objects.shop_disable()
        elif status == '2':
            shop_caring_lists = StaffCare.objects.filter(type=StaffCareType.STAFF_SHOP).values('shop')
            queryset = Shop.objects.shop_active().filter(~Q(pk__in=shop_caring_lists))
        else:
            if status == '3':
                shop_lists = ShopCube.objects.number_of_tran_this_week(value=1).values('shop_id')
            elif status == '4':
                shop_lists = ShopCube.objects.number_of_tran_this_week(value=2).values('shop_id')
            elif status == '5':
                shop_lists = ShopCube.objects.number_of_tran_this_week(value=3).values('shop_id')
            else:
                shop_lists = ShopCube.objects.number_of_tran_this_week(value=0).values('shop_id')
            queryset = Shop.objects.shop_active().filter(pk__in=shop_lists)
    else:
        queryset = Shop.objects.shop_active()

    if request.user.is_superuser is False:
        if request.user.is_area_manager or request.user.is_sale_admin:
            provinces = get_provinces_viewable_queryset(request.user)
            queryset = queryset.filter(province__in=provinces)
        else:
            shops = get_shops_viewable_queryset(request.user)
            queryset = queryset.filter(pk__in=shops)

    code = request.query_params.get('code', None)
    merchant_id = request.query_params.get('merchant_id', None)
    team_id = request.query_params.get('team_id', None)
    staff_id = request.query_params.get('staff_id', None)
    province_id = request.query_params.get('province_id', None)
    district_id = request.query_params.get('district_id', None)
    ward_id = request.query_params.get('ward_id', None)
    from_date = request.query_params.get('from_date', None)
    to_date = request.query_params.get('to_date', None)

    if code is not None and code != '':
        code = format_string(code)
        queryset = queryset.filter(code__icontains=code)

    if merchant_id is not None and merchant_id != '':
        queryset = queryset.filter(merchant_id=merchant_id)

    if team_id is not None and team_id != '':
        staffs = Staff.objects.filter(team=team_id)
        shop_ids = StaffCare.objects.filter(staff__in=staffs, type=StaffCareType.STAFF_SHOP).values('shop_id')
        queryset = queryset.filter(pk__in=shop_ids)

    if staff_id is not None and staff_id != '':
        shop_ids = StaffCare.objects.filter(staff=staff_id, type=StaffCareType.STAFF_SHOP).values('shop_id')
        queryset = queryset.filter(pk__in=shop_ids)

    if province_id is not None and province_id != '':
        queryset = queryset.filter(province=province_id)

    if district_id is not None and district_id != '':
        queryset = queryset.filter(district=district_id)

    if ward_id is not None and ward_id != '':
        queryset = queryset.filter(ward=ward_id)

    if from_date is not None and from_date != '':
        queryset = queryset.filter(
            created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
    if to_date is not None and to_date != '':
        queryset = queryset.filter(
            created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

    if len(queryset) > 2000:
        raise APIException(detail='Số lượng bản ghi quá lớn (>2.000), không thể xuất dữ liệu.', code=400)

    if len(queryset) == 0:
        return Shop.objects.none()

    return queryset

    # shop_ids = '('
    #
    # for shop in queryset.values('id'):
    #     shop_ids += str(shop['id']) + ','
    # shop_ids = shop_ids[:-1]
    # shop_ids += ')'
    #
    # sql_path = '/shop/management/sql_query/export_shop.txt'
    # f = open(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')) + sql_path, 'r')
    # raw_query = f.read()
    # raw_query += ' where s.id in ' + shop_ids
    #
    # return Shop.objects.raw(raw_query)

