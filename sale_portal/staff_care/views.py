import time
import json

from django.contrib.auth.decorators import login_required

from tablib import Dataset
from rest_framework.decorators import api_view

from sale_portal.shop.models import Shop
from sale_portal.staff.models import Staff
from sale_portal.staff_care.models import StaffCareImportLog
from sale_portal.common.standard_response import Code, successful_response, custom_response
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
    is_submit = request.POST.get('is_submit', None)
    submit_total_row = request.POST.get('submit_total_row', None)
    submit_total_row_not_change = request.POST.get('submit_total_row_not_change', None)
    submit_total_row_update = request.POST.get('submit_total_row_update', None)
    submit_total_row_error = request.POST.get('submit_total_row_error', None)

    is_submit = True if is_submit == 'true' else False

    try:
        imported_data = dataset.load(shop_file.read())
    except Exception as e:
        return custom_response(Code.FILE_TYPE_ERROR)

    data_error = []

    for item in imported_data:
        data = {
            'code': int(item[0]) if item[0] != '' else '',
            'address': item[1],
            'staff_email': str(item[2]).strip(),
        }
        total_row += 1
        result = update_sale_shop(request, data, is_submit)
        print(f'import_sale_shop: {result}')
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
            created_by=request.user
        ).save()
        data = f'Cập nhật thành công {row_update}/{total_row} bản ghi'
    else:
        data = {
            'total_row': total_row,
            'row_no_change': row_no_change,
            'row_update': row_update,
            'row_error': row_error,
            'path_data_error': render_excel_import_error(username=request.user.username, data=data_error)
        }

    return successful_response(data)


@login_required
def update_sale_shop(request, data, is_submit=False):
    # Các trường hợp lỗi:
    # 1. Thiếu shop Id hoặc không tìm thấy shop
    # 2. Thiếu staff_email hoặc không tìm thấy staff
    # 3. Staff bắt buộc phải thuộc team nào đó thì mới được gán vào shop, nếu không thì sẽ báo lỗi

    if data['code'] is None or str(data['code']) == '':
        return 'Shop_ID: Shop_ID trống - Lỗi dữ liệu'
    shop = Shop.objects.filter(code=str(data['code'])).first()
    if shop is None:
        return 'Shop_ID: Không tìm thấy Shop - Lỗi dữ liệu'

    if data['staff_email'] is None or data['staff_email'] == '':
        return 'Sale_email: Sale_email trống - Lỗi dữ liệu'
    staff = Staff.objects.filter(email=data['staff_email']).first()
    if staff is None:
        return 'Sale_email: Không tìm thấy Sale - Lỗi dữ liệu'
    if staff.team is None:
        return 'Sale không thuộc bất kì Team nào - Lỗi dữ liệu'

    if shop.staff == staff:
        return 'No change'

    else:
        if is_submit:
            if shop.staff:
                shop.staff_delete(request=request)
                shop.staff_create(staff_id=staff.id, request=request)
            else:
                shop.staff_create(staff_id=staff.id, request=request)
        return 'Thành công'


def render_excel_import_error(username='', data=[]):
    folder_name = 'sale-shop-import-error'
    file_name = str(username) + '_' + str(int(time.time())) + '.xlsx'
    sheet_name = 'DANH SÁCH BẢN GHI LỖI'

    column_headers = ['ShopID', 'Đường phố', 'Email Sale']

    return create_simple_excel_file(folder_name, file_name, sheet_name, column_headers, data)


@api_view(['POST'])
@login_required
def import_sale_merchant(request):
    """
        API import sale chăm sóc merchant bằng file excel
    """
    return
