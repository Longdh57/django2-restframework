import os
import time
import logging
import xlsxwriter

from django.db.models import Q
from django.utils import formats
from django.conf import settings
from django.db import connection
from rest_framework import viewsets, mixins
from datetime import datetime, date, timedelta
from rest_framework.decorators import api_view
from django.utils.html import conditional_escape
from rest_framework.exceptions import APIException
from django.contrib.auth.decorators import login_required, permission_required

from sale_portal.team import TeamType
from sale_portal.area.models import Area
from sale_portal.shop.models import Shop
from sale_portal.staff.models import Staff
from sale_portal.terminal.models import Terminal
from sale_portal.staff_care import StaffCareType
from sale_portal.staff_care.models import StaffCare
from sale_portal.utils.field_formatter import format_string
from sale_portal.terminal.serializers import TerminalSerializer
from sale_portal.qr_status.views import get_terminal_status_list
from sale_portal.utils.permission import get_user_permission_classes
from sale_portal.utils.data_export import ExportType, get_data_export
from sale_portal.utils.excel_util import check_or_create_excel_folder
from sale_portal.common.standard_response import successful_response, custom_response, Code
from sale_portal.utils.queryset import get_shops_viewable_queryset, get_provinces_viewable_queryset
from sale_portal.utils.refresh_shop_full_data import refresh_shop_full_data


class TerminalViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
        API get list Terminal \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - shop_id -- text
        - terminal_text -- text
        - merchant_id -- number
        - staff_id -- number
        - team_id -- number
        - area_id -- number
        - province_code -- text
        - district_code -- text
        - ward_code -- text
        - status -- number in {-1,1,2,3,4,5,6}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = TerminalSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('terminal.terminal_list_data', self.request)
        if self.action == 'retrieve':
            permission_classes = get_user_permission_classes('terminal.terminal_detail', self.request)
        if self.action == 'update':
            permission_classes = get_user_permission_classes('terminal.terminal_edit', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return get_queryset_terminal_list(self.request)

    def retrieve(self, request, pk):
        """
            API get detail Terminal
        """
        return detail(request, pk)

    def update(self, request, pk):
        """
            API update Terminal
        """
        return custom_response(Code.SUCCESS, "update method")


@api_view(['GET'])
@login_required
@permission_required('terminal.terminal_list_data', raise_exception=True)
def list_terminals(request):
    """
        API get list Terminal to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
        - merchant_id -- number
    """

    queryset = Terminal.objects.terminal_un_register_vnpayment()

    if request.user.is_superuser is False:
        if request.user.is_area_manager or request.user.is_sale_admin:
            provinces = get_provinces_viewable_queryset(request.user)
            queryset = queryset.filter(province_code__in=provinces.values('province_code'))
        else:
            shops = get_shops_viewable_queryset(request.user)
            queryset = queryset.filter(shop__in=shops)

    name = request.GET.get('name', None)
    merchant_id = request.GET.get('merchant_id', None)

    if name is not None and name != '':
        queryset = queryset.filter(Q(terminal_id__icontains=name) | Q(terminal_name__icontains=name))
    if merchant_id is not None and merchant_id != '':
        queryset = queryset.filter(merchant_id=merchant_id)

    queryset = queryset.order_by('terminal_name')[0:settings.PAGINATE_BY]

    data = [{'id': terminal.id, 'name': terminal.terminal_id + ' - ' + terminal.terminal_name} for
            terminal in queryset]

    return successful_response(data)


def detail(request, pk):
    try:
        if request.user.is_superuser is False:
            if request.user.is_area_manager or request.user.is_sale_admin:
                provinces = get_provinces_viewable_queryset(request.user)
                terminal = Terminal.objects.filter(pk=pk, province_code__in=provinces.values('province_code')).first()
            else:
                shops = get_shops_viewable_queryset(request.user)
                terminal = Terminal.objects.filter(pk=pk, shop__in=shops).first()
        else:
            terminal = Terminal.objects.filter(pk=pk).first()

        if terminal is None:
            return custom_response(Code.TERMINAL_NOT_FOUND)

        merchant = terminal.merchant
        shop = terminal.shop
        staff = shop.staff if shop else None
        team = staff.team if staff else None
        staff_chain = shop.staff_of_chain if shop else None
        team_chain = staff_chain.team if staff_chain else None

        data = {
            'id': terminal.id,
            'terminal_id': terminal.terminal_id,
            'terminal_name': terminal.terminal_name,
            'terminal_address': terminal.terminal_address,
            'province': {'id': terminal.get_province().id,
                         'name': terminal.get_province().province_name,
                         'code': terminal.get_province().province_code} if terminal.get_province() else None,
            'district': {'id': terminal.get_district().id,
                         'name': terminal.get_district().district_name,
                         'code': terminal.get_district().district_code} if terminal.get_district() else None,
            'wards': {'id': terminal.get_wards().id,
                      'name': terminal.get_wards().wards_name,
                      'code': terminal.get_wards().wards_code} if terminal.get_wards() else None,
            'business_address': terminal.business_address,
            'merchant': {
                'id': merchant.id if merchant else '',
                'name': merchant.merchant_name if merchant else '',
                'code': merchant.merchant_code if merchant else '',
                'brand': merchant.merchant_brand if merchant else '',
            },
            'shop': {
                'id': shop.id if shop else '',
                'name': shop.name if shop else '',
                'code': shop.code if shop else '',
                'address': shop.address if shop else '',
                'street': shop.street if shop else '',
                'take_care_status': shop.take_care_status if shop else '',
                'activated': shop.activated if shop else '',
                'province_name': shop.province.province_name if (shop and shop.province) else '',
                'district_name': shop.district.district_name if (shop and shop.district) else '',
                'wards_name': shop.wards.wards_name if (shop and shop.wards) else '',
                'staff': {
                    'id': staff.id if staff else None,
                    'full_name': staff.full_name if staff else '',
                    'email': staff.email if staff else ''
                },
                'team': {
                    'id': team.id if team else None,
                    'code': team.code if team else '',
                    'name': team.name if team else ''
                },
                'staff_chain': {
                    'id': staff_chain.id if staff_chain else None,
                    'full_name': staff_chain.full_name if staff_chain else '',
                    'email': staff_chain.email if staff_chain else ''
                },
                'team_chain': {
                    'id': team_chain.id if team_chain else None,
                    'code': team_chain.code if team_chain else '',
                    'name': team_chain.name if team_chain else ''
                }
            },
            'created_date': formats.date_format(terminal.created_date,
                                                "SHORT_DATETIME_FORMAT") if terminal.created_date else '',
            'status': int(terminal.get_status()) if terminal.get_status() else None,
        }
        return successful_response(data)
    except Exception as e:
        logging.error('Get detail terminal exception: %s', e)
        return custom_response(Code.INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@login_required
def list_status(request):
    """
        API get list status of Terminal
    """
    return successful_response(get_terminal_status_list())


@api_view(['POST'])
@login_required
def create_shop_from_terminal(request):
    """
        API create shop from Terminal \n
        Parameters for this api : Required
        - terminal_id -- number
        - address -- text
        - street -- text
    """
    shop_store(request)


def shop_store(request):
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

    if terminal.register_vnpayment == 1:
        return

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

    refresh_shop_full_data()

    return successful_response(data)


@api_view(['GET'])
@login_required
@permission_required('terminal.dashboard_terminal_count', raise_exception=True)
def count_terminal_30_days_before(request):
    all_terminal = request.GET.get('all_terminal', None)

    if all_terminal is not None and all_terminal != '':
        terminal_count = Terminal.objects.filter(~Q(status=-1) & ~Q(register_vnpayment=1)).count()
    else:
        terminal_count = Terminal.objects.filter(Q(status=1) & ~Q(register_vnpayment=1)).count()

    with connection.cursor() as cursor:
        cursor.execute('''
            select count(*), date(created_date)
            from terminal
            where created_date > current_date - interval '30 days' and register_vnpayment <> 1 and status <> -1
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
    yesterday = 0
    for item in data_cursor:
        if str(item['date']) == str((date.today() - timedelta(days=1)).strftime("%Y-%m-%d")):
            yesterday = item['count']
        data_date.append(str(item['date'].strftime("%d/%m/%Y")))
        data_value.append(item['count'])

    return successful_response({
        'data': {
            'data_date': data_date,
            'data_value': data_value
        },
        'yesterday': yesterday,
        'terminal_count': terminal_count
    })


@api_view(['GET'])
@login_required
@permission_required('terminal.dashboard_terminal_count', raise_exception=True)
def count_terminal_30_days_before_heatmap(request):
    today = date.today()
    date_list = []
    hour_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    for i in range(0, 14):
        date_list.append((today - timedelta(days=14) + timedelta(days=i)).strftime("%d/%m/%Y"))

    with connection.cursor() as cursor:
        cursor.execute('''
            select  count(*),date(created_date) as terminal_date, extract(hour from created_date) as terminal_hour
            from terminal
            where created_date > current_date - interval '14 days' and created_date < current_date
            group by terminal_date,terminal_hour
            order by date(created_date) asc
        ''')
        columns = [col[0] for col in cursor.description]
        data_cursor = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    data = []
    for item in data_cursor:
        data.append([
            date_list.index(str(item['terminal_date'].strftime("%d/%m/%Y"))),
            hour_list.index(item['terminal_hour']),
            item['count']
        ])

    return successful_response({
        'data': data,
        'date_list': date_list,
        'hour_list': hour_list
    })


@api_view(['GET'])
@login_required
@permission_required('terminal.terminal_export', raise_exception=True)
def export(request):
    """
        API export data Terminal \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - shop_id -- text
        - terminal_text -- text
        - merchant_id -- number
        - staff_id -- number
        - team_id -- number
        - area_id -- number
        - province_code -- text
        - district_code -- text
        - ward_code -- text
        - status -- number in {-1,1,2,3,4,5,6}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """

    file_path = render_excel(request)

    return successful_response(file_path)


@login_required
def render_excel(request=None, return_url=True):
    check_or_create_excel_folder()

    if not os.path.exists(settings.MEDIA_ROOT + '/excel/terminal'):
        os.mkdir(os.path.join(settings.MEDIA_ROOT + '/excel', 'terminal'))

    file_name = 'terminal_' + str(int(time.time())) + '.xlsx'
    workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + '/excel/terminal/' + file_name)
    worksheet = workbook.add_worksheet('DANH SÁCH TERMINAL')

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
    worksheet.write('A1', 'Terminal ID', merge_format)
    worksheet.write('B1', 'Terminal Name', merge_format)
    worksheet.write('C1', 'Merchant Code', merge_format)
    worksheet.write('D1', 'Merchant Brand', merge_format)
    worksheet.write('E1', 'Merchant Name', merge_format)
    worksheet.write('F1', 'Sale ký HĐ MC', merge_format)
    worksheet.write('G1', 'Shop Code', merge_format)
    worksheet.write('H1', 'Nhân viên (Phụ trách Shop)', merge_format)
    worksheet.write('I1', 'Team', merge_format)
    worksheet.write('J1', 'Địa chỉ', merge_format)
    worksheet.write('K1', 'Tỉnh thành', merge_format)
    worksheet.write('L1', 'Quận huyện', merge_format)
    worksheet.write('M1', 'Phường xã', merge_format)
    worksheet.write('N1', 'Ngày tạo', merge_format)
    worksheet.freeze_panes(1, 0)

    terminals = get_terminal_exports(request)

    row_num = 1
    for item in terminals:
        worksheet.write(row_num, 0, item['terminal_id'])
        worksheet.write(row_num, 1, item['terminal_name'] if item['terminal_name'] else '')
        worksheet.write(row_num, 2, item['merchant_code'] if item['merchant_code'] else '')
        worksheet.write(row_num, 3, item['merchant_brand'] if item['merchant_brand'] else '')
        worksheet.write(row_num, 4, item['merchant_name'] if item['merchant_name'] else '')
        worksheet.write(row_num, 5, item['email'] if item['email'] else '')
        worksheet.write(row_num, 6, item['shop_code'] if item['shop_code'] else '')
        worksheet.write(row_num, 7, item['staff_email'] if item['staff_email'] else '')
        worksheet.write(row_num, 8, item['team_code'] if item['team_code'] else '')
        worksheet.write(row_num, 9, item['business_address'] if item['business_address'] else '')
        worksheet.write(row_num, 10, item['province_name'] if item['province_name'] else '')
        worksheet.write(row_num, 11, item['district_name'] if item['district_name'] else '')
        worksheet.write(row_num, 12, item['wards_name'] if item['wards_name'] else '')
        worksheet.write(row_num, 13,
                        formats.date_format(item['created_date'], "SHORT_DATETIME_FORMAT") if item[
                            'created_date'] else '')

        row_num += 1

    workbook.close()

    if return_url:
        return settings.MEDIA_URL + '/excel/terminal/' + file_name
    return settings.MEDIA_ROOT + '/excel/terminal/' + file_name


def get_terminal_exports(request):
    queryset = get_queryset_terminal_list(request)

    if len(queryset) > 15000 and request.user.is_superuser is False:
        raise APIException(detail='Số lượng bản ghi quá lớn (>15.000), không thể xuất dữ liệu.', code=400)

    if len(queryset) == 0:
        return Terminal.objects.none()

    return get_data_export(queryset, ExportType.TERMINAL)


def get_queryset_terminal_list(request):
    queryset = Terminal.objects.terminal_un_register_vnpayment()

    if request.user.is_superuser is False:
        if request.user.is_area_manager or request.user.is_sale_admin:
            # Neu la SM (or SA) cua tripi, teko thi load ds shop => ds ter
            if request.user.is_manager_outside_vnpay:
                shops = get_shops_viewable_queryset(request.user)
                queryset = queryset.filter(shop__in=shops)
            # Neu la SM (or SA) cua Vnpay thi load ds provinces => ds ter
            else:
                provinces = get_provinces_viewable_queryset(request.user)
                queryset = queryset.filter(province_code__in=provinces.values('province_code'))
        else:
            shops = get_shops_viewable_queryset(request.user)
            queryset = queryset.filter(shop__in=shops)

    shop_id = request.query_params.get('shop_id', None)
    terminal_text = request.query_params.get('terminal_text', None)
    area_id = request.query_params.get('area_id', None)
    merchant_id = request.query_params.get('merchant_id', None)
    staff_id = request.query_params.get('staff_id', None)
    team_id = request.query_params.get('team_id', None)
    status = request.query_params.get('status', None)
    province_code = request.query_params.get('province_code', None)
    district_code = request.query_params.get('district_code', None)
    ward_code = request.query_params.get('ward_code', None)
    from_date = request.query_params.get('from_date', None)
    to_date = request.query_params.get('to_date', None)
    assign_shop = request.query_params.get('assign_shop', None)

    if shop_id is not None and shop_id != '':
        shop_id = format_string(shop_id)
        queryset = queryset.filter(shop_id=shop_id)

    if terminal_text is not None and terminal_text != '':
        terminal_text = format_string(terminal_text)
        queryset = queryset.filter(
            Q(terminal_id__icontains=terminal_text) | Q(terminal_name__icontains=terminal_text))

    if area_id is not None and area_id != '':
        if area_id.isdigit():
            province_codes = []
            area = Area.objects.get(pk=int(area_id))
            provinces = area.get_provinces()
            for item in provinces:
                province_codes.append(item.province_code)
            queryset = queryset.filter(province_code__in=province_codes)

    if merchant_id is not None and merchant_id != '':
        queryset = queryset.filter(merchant_id=merchant_id)

    if staff_id is not None and staff_id != '':
        shops = StaffCare.objects.filter(staff_id=staff_id, type=StaffCareType.STAFF_SHOP).values('shop')
        queryset = queryset.filter(shop__in=shops)

    if team_id is not None and team_id != '':
        staffs = Staff.objects.filter(team_id=team_id)
        shops = StaffCare.objects.filter(staff__in=staffs, type=StaffCareType.STAFF_SHOP).values('shop')
        queryset = queryset.filter(shop__in=shops)

    if status is not None and status != '':
        queryset = queryset.filter(status=int(status))

    if province_code is not None and province_code != '':
        queryset = queryset.filter(province_code=province_code)

    if district_code is not None and district_code != '':
        queryset = queryset.filter(district_code=district_code)

    if ward_code is not None and ward_code != '':
        queryset = queryset.filter(wards_code=ward_code)

    if assign_shop is not None and assign_shop != '':
        if assign_shop == '1':
            queryset = queryset.filter(shop__isnull=False)
        else:
            queryset = queryset.filter(shop__isnull=True)

    if from_date is not None and from_date != '':
        queryset = queryset.filter(
            created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))

    if to_date is not None and to_date != '':
        queryset = queryset.filter(
            created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

    return queryset
