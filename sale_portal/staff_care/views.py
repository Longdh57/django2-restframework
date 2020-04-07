import json
import time
from datetime import datetime

from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from tablib import Dataset

from sale_portal import settings
from sale_portal.common.standard_response import Code, successful_response, custom_response
from sale_portal.merchant.models import Merchant
from sale_portal.shop.models import Shop
from sale_portal.staff.models import Staff, QrStaff
from sale_portal.staff_care import StaffCareType
from sale_portal.staff_care.models import StaffCareImportLog
from sale_portal.staff_care.serializers import StaffCareImportLogSerializer
from sale_portal.utils.excel_util import check_or_create_excel_folder, create_simple_excel_file


@api_view(['POST'])
@login_required
def import_sale_shop(request):
    """
        API import sale chăm sóc shop bằng file excel \n
        Request body for this api : Định dạng form-data \n
            "shop_file": file_excel_upload,
            "submit_total_row": 10,
            "submit_total_row_not_change": 2,
            "submit_total_row_update": 7,
            "submit_total_row_error": 1,
            "is_submit": true/false \n
    """
    dataset = Dataset()

    total_row, row_no_change, row_update, row_error = 0, 0, 0, 0

    shop_file = request.FILES['shop_file']
    data = json.loads(request.POST.get('data', None))

    is_submit = data.get('is_submit', None)
    submit_total_row = data.get('submit_total_row', None)
    submit_total_row_not_change = data.get('submit_total_row_not_change', None)
    submit_total_row_update = data.get('submit_total_row_update', None)
    submit_total_row_error = data.get('submit_total_row_error', None)

    is_submit = True if is_submit == 'true' else False

    try:
        imported_data = dataset.load(shop_file.read())
    except Exception as e:
        return custom_response(Code.FILE_TYPE_ERROR)

    data_error = []

    ocg_staff_ids = QrStaff.objects.filter(email__in=settings.LIST_OCG_EMAIL).values('staff_id')
    ocg_merchants = Merchant.objects.filter(staff__in=ocg_staff_ids)
    ocg_shops = Shop.objects.filter(merchant__in=ocg_merchants).values('id')

    ocg_shop_ids = []
    for ocg_shop in ocg_shops:
        ocg_shop_ids.append(ocg_shop['id'])

    for item in imported_data:
        data = {
            'code': int(item[0]) if (isinstance(item[0], int) and item[0] != '') else '',
            'street': item[1],
            'staff_email': str(item[2]).strip() if item[2] else '',
        }
        total_row += 1
        if isinstance(item[0], int) and int(item[0]) in ocg_shop_ids:
            result = 'Shop này do OCG khai thác'
        else:
            result = update_sale_shop(request, data, is_submit)

        if result == 'Thành công':
            row_update += 1
        elif result == 'No change':
            row_no_change += 1
        else:
            row_error += 1
            data['update_status'] = result
            data_error.append(data)

    if is_submit:
        check_or_create_excel_folder()
        description = json.dumps(dict(
            total_row=submit_total_row,
            row_no_change=submit_total_row_not_change,
            row_update=submit_total_row_update,
            row_error=submit_total_row_error
        ))
        StaffCareImportLog(
            file_url=shop_file,
            description=description,
            type=StaffCareType.STAFF_SHOP,
            created_by=request.user
        ).save()
        data = f'Cập nhật thành công {row_update}/{total_row} bản ghi'
    else:
        data = {
            'total_row': total_row,
            'row_no_change': row_no_change,
            'row_update': row_update,
            'row_error': row_error,
            'path_data_error': sale_shop_render_excel_import_error(username=request.user.username, data=data_error)
        }

    return successful_response(data)


@login_required
def update_sale_shop(request, data, is_submit=False):
    # Các trường hợp lỗi:
    # 1. Thiếu shop Id hoặc không tìm thấy shop
    # 2. Thiếu staff_email hoặc không tìm thấy staff
    # 3. Staff bắt buộc phải thuộc team nào đó thì mới được gán vào shop, nếu không thì sẽ báo lỗi
    # 4. Đường phố nếu để rỗng thì không làm gì cả, nếu đường phố khác rỗng thì update đường phố vào shop

    if data['code'] is None or str(data['code']) == '':
        return 'Shop_ID: Shop_ID trống - Lỗi dữ liệu'
    shop = Shop.objects.filter(code=str(data['code'])).first()
    if shop is None:
        return 'Shop_ID: Không tìm thấy Shop - Lỗi dữ liệu'

    if data['staff_email'] is None or data['staff_email'] == '':
        if is_submit:
            if shop.staff:
                shop.staff_delete(request=request)
            if data['street'] != '' and data['street'] is not None:
                shop.street = data['street']
                shop.save()
        return 'Thành công'
    else:
        staff = Staff.objects.filter(email=data['staff_email']).first()
        if staff is None:
            return 'Sale_email: Không tìm thấy Sale - Lỗi dữ liệu'
        if staff.team is None:
            return 'Sale không thuộc bất kì Team nào - Lỗi dữ liệu'

        if shop.staff == staff and (data['street'] == '' or data['street'] is None):
            return 'No change'
        elif shop.staff == staff and (data['street'] != '' and data['street'] is not None):
            if is_submit:
                shop.street = data['street']
                shop.save()
            return 'Thành công'
        else:
            if is_submit:
                if data['street'] != '':
                    shop.street = data['street']
                    shop.save()

                if shop.staff:
                    shop.staff_delete(request=request)
                    shop.staff_create(staff_id=staff.id, request=request)
                else:
                    shop.staff_create(staff_id=staff.id, request=request)
            return 'Thành công'



def sale_shop_render_excel_import_error(username='', data=[]):
    folder_name = 'sale-shop-import-error'
    file_name = str(username) + '_' + str(int(time.time())) + '.xlsx'
    sheet_name = 'DANH SÁCH BẢN GHI LỖI'

    column_headers = ['ShopID', 'Đường phố', 'Email Sale']

    return create_simple_excel_file(folder_name, file_name, sheet_name, column_headers, data)


@api_view(['POST'])
@login_required
def import_sale_merchant(request):
    """
        API import sale chăm sóc merchant bằng file excel \n
        Request body for this api : Định dạng form-data \n
            "merchant_file": file_excel_upload,
            "submit_total_row": 10,
            "submit_total_row_not_change": 2,
            "submit_total_row_update": 7,
            "submit_total_row_error": 1,
            "is_submit": true/false \n
    """
    dataset = Dataset()

    total_row, row_no_change, row_update, row_error = 0, 0, 0, 0

    merchant_file = request.FILES['merchant_file']
    data = json.loads(request.POST.get('data', None))

    is_submit = data.get('is_submit', None)
    submit_total_row = data.get('submit_total_row', None)
    submit_total_row_not_change = data.get('submit_total_row_not_change', None)
    submit_total_row_update = data.get('submit_total_row_update', None)
    submit_total_row_error = data.get('submit_total_row_error', None)

    is_submit = True if is_submit == 'true' else False

    try:
        imported_data = dataset.load(merchant_file.read())
    except Exception as e:
        return custom_response(Code.FILE_TYPE_ERROR)

    data_error = []

    for item in imported_data:
        data = {
            'merchant_code': str(item[0]).strip(),
            'staff_email': str(item[1]).strip(),
        }
        total_row += 1
        result = update_sale_merchant(request, data, is_submit)

        if result == 'Thành công':
            row_update += 1
        elif result == 'No change':
            row_no_change += 1
        else:
            row_error += 1
            data['update_status'] = result
            data_error.append(data)

    if is_submit:
        check_or_create_excel_folder()
        description = json.dumps(dict(
            total_row=submit_total_row,
            row_no_change=submit_total_row_not_change,
            row_update=submit_total_row_update,
            row_error=submit_total_row_error
        ))
        StaffCareImportLog(
            file_url=merchant_file,
            description=description,
            type=StaffCareType.STAFF_MERCHANT,
            created_by=request.user
        ).save()
        data = f'Cập nhật thành công {row_update}/{total_row} bản ghi'
    else:
        data = {
            'total_row': total_row,
            'row_no_change': row_no_change,
            'row_update': row_update,
            'row_error': row_error,
            'path_data_error': sale_merchant_render_excel_import_error(username=request.user.username, data=data_error)
        }

    return successful_response(data)


@login_required
def update_sale_merchant(request, data, is_submit=False):
    # Các trường hợp lỗi:
    # 1. Thiếu merchant_code hoặc không tìm thấy merchant
    # 2. Thiếu staff_email hoặc không tìm thấy staff
    # 3. Staff bắt buộc phải thuộc team nào đó thì mới được gán vào merchant, nếu không thì sẽ báo lỗi

    if data['merchant_code'] is None or data['merchant_code'] == '':
        return 'Merchant_code: Merchant_code trống - Lỗi dữ liệu'
    merchant = Merchant.objects.filter(merchant_code=str(data['merchant_code'])).first()
    if merchant is None:
        return 'Merchant_code: Không tìm thấy Merchant - Lỗi dữ liệu'

    if data['staff_email'] is None or data['staff_email'] == '':
        return 'Sale_email: Sale_email trống - Lỗi dữ liệu'
    staff = Staff.objects.filter(email=data['staff_email']).first()
    if staff is None:
        return 'Sale_email: Không tìm thấy Sale - Lỗi dữ liệu'
    if staff.team is None:
        return 'Sale không thuộc bất kì Team nào - Lỗi dữ liệu'

    if merchant.staff_care == staff:
        return 'No change'

    else:
        if is_submit:
            if merchant.staff_care:
                merchant.staff_delete(request=request)
                merchant.staff_create(staff_id=staff.id, request=request)
            else:
                merchant.staff_create(staff_id=staff.id, request=request)
        return 'Thành công'


def sale_merchant_render_excel_import_error(username='', data=[]):
    folder_name = 'sale-merchant-import-error'
    file_name = str(username) + '_' + str(int(time.time())) + '.xlsx'
    sheet_name = 'DANH SÁCH BẢN GHI LỖI'

    column_headers = ['Merchant Code', 'Email Sale']

    return create_simple_excel_file(folder_name, file_name, sheet_name, column_headers, data)


class StaffCareImportLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get danh sách lịch sử Import file  \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - type -- number {0,1,2}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = StaffCareImportLogSerializer

    def get_queryset(self):

        queryset = StaffCareImportLog.objects.all()

        type = self.request.query_params.get('type', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if type is not None and type != '':
            queryset = queryset.filter(type=type)
        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

        return queryset
