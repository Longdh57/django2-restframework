import logging
import json
import time
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import formats
from django.conf import settings

from sale_portal.utils.permission import get_user_permission_classes
from .serializers import SalePromotionSerializer
from tablib import Dataset

from .models import SalePromotion, SalePromotionTitle
from ..staff.models import Staff
from ..terminal.models import Terminal
from ..shop.models import Shop
from ..utils.excel_util import create_simple_excel_file
from ..common.standard_response import successful_response, custom_response, Code


class SalePromotionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list SalePromotion   \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - title_id -- integer
        - terminal_id -- text
        - shop_code -- text
        - team_id -- integer
        - staff_id -- integer
        - status -- number in {0, 1, 2, 3}
    """
    serializer_class = SalePromotionSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('sale_promotion_form.sale_promotion_list_data', self.request)
        if self.action == 'retrieve':
            permission_classes = get_user_permission_classes('sale_promotion_form.sale_promotion_detail', self.request)
        if self.action == 'update':
            permission_classes = get_user_permission_classes('sale_promotion_form.sale_promotion_edit', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        title_id = self.request.query_params.get('title_id', None)
        terminal_id = self.request.query_params.get('terminal_id', None)
        shop_code = self.request.query_params.get('shop_code', None)
        staff_id = self.request.query_params.get('staff_id', None)
        team_id = self.request.query_params.get('team_id', None)
        status = self.request.query_params.get('status', None)

        queryset = SalePromotion.objects.all()

        if title_id is not None and title_id != '':
            queryset = queryset.filter(title_id=title_id)
        if terminal_id is not None and terminal_id != '':
            terminals = Terminal.objects.filter(terminal_id__icontains=terminal_id)
            queryset = queryset.filter(terminal__in=terminals)
        if shop_code is not None and shop_code != '':
            shops = Shop.objects.filter(code__icontains=shop_code)
            queryset = queryset.filter(shop__in=shops)
        if staff_id is not None and staff_id != '':
            queryset = queryset.filter(staff_id=staff_id)
        if team_id is not None and team_id != '':
            staffs = Staff.objects.filter(team_id=team_id)
            queryset = queryset.filter(staff__in=staffs)
        if status is not None and status != '':
            queryset = queryset.filter(status=status)

        return queryset

    def retrieve(self, request, pk):
        """
            API get detail SalePromotion
        """
        sale_promotion = SalePromotion.objects.filter(pk=pk).first()

        if sale_promotion is None:
            return custom_response(Code.PROMOTION_NOT_FOUND)

        data = {
            'merchant': sale_promotion.get_merchant(),
            'terminal': sale_promotion.get_terminal(),
            'shop': sale_promotion.get_shop(),
            'staff': sale_promotion.get_staff(),
            'title': sale_promotion.get_title(),
            'contact_person': sale_promotion.contact_person,
            'contact_phone_number': sale_promotion.contact_phone_number,
            'contact_email': sale_promotion.contact_email,
            'tentcard_ctkm': sale_promotion.tentcard_ctkm,
            'wobbler_ctkm': sale_promotion.wobbler_ctkm,
            'status': sale_promotion.get_status(),
            'image': sale_promotion.image if sale_promotion.image else '',
            'sub_image': sale_promotion.sub_image if sale_promotion.sub_image else '',
            'created_date': formats.date_format(sale_promotion.created_date,
                                                "SHORT_DATETIME_FORMAT") if sale_promotion.created_date else '',
            'updated_date': formats.date_format(sale_promotion.updated_date,
                                                "SHORT_DATETIME_FORMAT") if sale_promotion.updated_date else ''
        }

        return successful_response(data)

    def update(self, request, pk):
        """
            API update SalePromotion \n
            Request body for this api : Định dạng json \n
                {
                    "tentcard_ctkm": true/false,
                    "wobbler_ctkm": true/false,
                    "status": 2 (status in {0,1,2,3} ),
                    "image": "text",
                    "sub_image": "text"
                }
        """
        sale_promotion = SalePromotion.objects.filter(pk=pk).first()
        if sale_promotion is None:
            return custom_response(Code.PROMOTION_NOT_FOUND)

        body = json.loads(request.body)

        status = body.get('status')
        tentcard_ctkm = body.get('tentcard_ctkm')
        wobbler_ctkm = body.get('wobbler_ctkm')
        image = body.get('image')
        sub_image = body.get('sub_image')

        try:
            status = int(status) if status is not None else None
        except ValueError:
            return custom_response(Code.STATUS_NOT_VALID)

        if status is None or not 0 <= status <= 3:
            return custom_response(Code.STATUS_NOT_VALID)

        tentcard_ctkm = True if tentcard_ctkm is not None and tentcard_ctkm == 'true' else False
        wobbler_ctkm = True if wobbler_ctkm is not None and wobbler_ctkm == 'true' else False

        if image is not None and image != '':
            sale_promotion.image = image

        elif status != 0 and (sale_promotion.image is None or sale_promotion.image == ''):
            return custom_response(Code.BAD_REQUEST, 'Cần upload ảnh nghiệm thu với trạng thái hiện tại của shop')

        if sub_image is not None and sub_image != '':
            sale_promotion.sub_image = sub_image

        sale_promotion.status = status
        sale_promotion.tentcard_ctkm = tentcard_ctkm
        sale_promotion.wobbler_ctkm = wobbler_ctkm
        sale_promotion.updated_by = request.user

        sale_promotion.save()
        return successful_response()


@api_view(['POST'])
@login_required
@permission_required('sale_promotion_form.sale_promotion_import', raise_exception=True)
def import_view(request):
    """
        API import SalePromotion \n
        Request body for this api : Định dạng form-data \n
            "promotion_file": file_excel_upload,
            "title_id": 2,
            "title_code": "title_code",
            "title_description": "title_description",
            "is_submit": true/false \n
    """
    dataset = Dataset()

    promotion_file = request.FILES['promotion_file']
    data = request.POST.get('data', None)
    if data is None:
        return custom_response(Code.CANNOT_READ_DATA_BODY)
    try:
        data_json = json.loads(data)
    except Exception as e:
        logging.error(e)
        return custom_response(Code.CANNOT_CONVERT_DATA_BODY)

    title_id = data_json['title_id'] if 'title_id' in data_json else None
    title_code = data_json['title_code'] if 'title_code' in data_json else None
    title_description = data_json['title_description'] if 'title_description' in data_json else None
    is_submit = data_json['is_submit'] if 'is_submit' in data_json else None

    is_submit = True if is_submit == 'true' else False

    if title_id is not None and title_id != '':
        promotion_title = SalePromotionTitle.objects.filter(pk=title_id).first()
        if promotion_title is None:
            return custom_response(Code.PROMOTION_TITLE_NOT_FOUND)
    else:
        if title_code is None or title_code == '':
            return custom_response(Code.INVALID_BODY, 'title_code invalid')
        promotion_title = SalePromotionTitle.objects.filter(code__iexact=title_code).first()
        if promotion_title is not None:
            return custom_response(Code.BAD_REQUEST, 'title_code be used by other PromotionTitle')
        promotion_title = SalePromotionTitle(
            code=title_code.upper(),
            description=title_description
        )
        if is_submit:
            promotion_title.save()

    try:
        promotion_rows = dataset.load(promotion_file.read())
    except Exception as e:
        logging.error('Promotion import file exception: %s', e)
        return custom_response(Code.INVALID_BODY, 'Nội dung file sai định dạng, vui lòng tải file mẫu và làm theo.')

    total_row = 0
    row_create = 0
    row_no_change = 0
    row_update = 0
    row_error = 0
    data_error = []

    for item in promotion_rows:
        data = {
            'terminal_id': item[0],
            'shop_code': item[1],
            'staff_email': item[2],
            'contact_person': item[3],
            'contact_phone_number': item[4],
            'contact_email': item[5],
            'update_status': ''
        }
        total_row += 1
        result = import_view_update_action(data, request, is_submit, promotion_title)
        if result == 'Tạo mới':
            row_create += 1
        elif result == 'Update staff' or result == 'Update contact info':
            row_update += 1
        elif result == 'No change':
            row_no_change += 1
        else:
            row_error += 1
            data['update_status'] = result
            data_error.append(data)

    if is_submit:
        data = "Cập nhật thành công " + str(row_create + row_update) + "/" + str(total_row) + " bản ghi"
    else:
        data = {
            'total_row': total_row,
            'row_create': row_create,
            'row_no_change': row_no_change,
            'row_update': row_update,
            'row_error': row_error,
            'path_data_error': render_excel_import_error(request.user, data_error)
        }
    return successful_response(data)


def import_view_update_action(data, request, is_submit=False, promotion_title=None):
    if data['terminal_id'] is None or str(data['terminal_id']) == '':
        return 'Terminal_ID: Terminal_ID trống - Lỗi dữ liệu'
    if data['shop_code'] is None or str(data['shop_code']) == '':
        return 'shop_code: shop_code trống - Lỗi dữ liệu'
    if data['staff_email'] is None or str(data['staff_email']) == '':
        return 'Sale: Sale trống - Lỗi dữ liệu'
    terminal = Terminal.objects.filter(terminal_id=data['terminal_id']).first()
    if terminal is None:
        return 'Terminal_ID: Không tìm thấy Terminal'
    shop = Shop.objects.filter(code=data['shop_code']).first()
    if shop is None:
        return 'shop_code: Không tìm thấy Shop'
    if terminal.shop != shop:
        return 'Terminal-Shop: Terminal không được gán với Shop'
    staff = Staff.objects.filter(email=data['staff_email']).first()
    if staff is None:
        return 'Sale: Không tìm thấy Sale'

    if isinstance(data['contact_phone_number'], float):
        data['contact_phone_number'] = str(int(data['contact_phone_number']))

    promotion = SalePromotion.objects.filter(terminal=terminal, shop=shop, title=promotion_title).first()

    if promotion is None:
        if is_submit:
            promotion = SalePromotion(
                terminal=terminal,
                shop=shop,
                staff=staff,
                title=promotion_title,
                contact_person=str(data['contact_person']) if data['contact_person'] is not None else '',
                contact_phone_number=str(data['contact_phone_number']) if data['contact_phone_number'] is not None else '',
                contact_email=str(data['contact_email']) if data['contact_email'] is not None else '',

                tentcard_ctkm=False,
                wobbler_ctkm=False,
                status=0,
                created_by=request.user,
                updated_by=request.user
            )
            promotion.save()
        return 'Tạo mới'

    else:
        if promotion.staff == staff and promotion.contact_person == str(
                data['contact_person']) and promotion.contact_phone_number == str(
                data['contact_phone_number']) and promotion.contact_email == str(data['contact_email']):
            return 'No change'
        elif promotion.staff != staff:
            message = 'Update staff'
        else:
            message = 'Update contact info'
        if is_submit:
            promotion.staff = staff
            promotion.contact_person = str(data['contact_person']) if data['contact_person'] is not None else ''
            promotion.contact_phone_number = str(data['contact_phone_number']) if data['contact_phone_number'] is not None else ''
            promotion.contact_email = str(data['contact_email']) if data['contact_email'] is not None else ''
            promotion.updated_by = request.user
            promotion.save()
        return message


@api_view(['GET'])
@login_required
@permission_required('sale_promotion_form.promotion_title_list_data', raise_exception=True)
def get_list_titles(request):
    """
       API get list Title to select \n
       Parameters for this api : Có thể bỏ trống hoặc không gửi lên
       - code -- text
    """

    queryset = SalePromotionTitle.objects.all()

    code = request.GET.get('code', None)

    if code is not None and code != '':
        queryset = queryset.filter(code__icontains=code)

    queryset = queryset.order_by('code')[0:settings.PAGINATE_BY]

    data = [{'id': title.id, 'content': title.code + ' - ' + (title.description if title.description else 'N/A')} for title in queryset]

    return successful_response(data)


@api_view(['DELETE'])
@login_required
@permission_required('sale_promotion_form.sale_promotion_reset_data', raise_exception=True)
def reset_data(request):
    """
        API delete all SalePromotion
    """
    SalePromotion.objects.all().delete()

    return successful_response()


def render_excel_import_error(staff_email='', data=[]):

    folder_name = 'sale-promotion-import-error'
    file_name = str(staff_email) + '_' + str(int(time.time())) + '.xlsx'
    sheet_name = 'DANH SÁCH BẢN GHI LỖI'

    column_headers = ['Terminal_ID', 'Shop_code', 'Sale', 'Người lien hệ', 'SĐT liên hệ', 'Email liên hệ']

    return create_simple_excel_file(folder_name, file_name, sheet_name, column_headers, data)
