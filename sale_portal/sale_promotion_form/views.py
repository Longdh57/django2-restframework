import logging
import time
import datetime
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import formats
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from .serializers import SalePromotionSerializer
from tablib import Dataset

from .models import SalePromotion, SalePromotionTitle
from ..staff.models import Staff
from ..terminal.models import Terminal
from ..shop.models import Shop
from ..utils.excel_util import create_simple_excel_file


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
        Có thể bỏ trống
    """
    serializer_class = SalePromotionSerializer

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
            queryset = queryset.filter(termail__in=terminals)
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
        sale_promotion = SalePromotion.objects.filter(pk=pk)

        if not sale_promotion:
            return JsonResponse({
                'status': 404,
                'message': 'SalePromotion not found'
            }, status=404)

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
            'image': sale_promotion.image.url if sale_promotion.image else '',
            'sub_image': sale_promotion.image.url if sale_promotion.image else '',
            'created_date': formats.date_format(sale_promotion.created_date,
                                                "SHORT_DATETIME_FORMAT") if sale_promotion.created_date else '',
            'updated_date': formats.date_format(sale_promotion.updated_date,
                                                "SHORT_DATETIME_FORMAT") if sale_promotion.updated_date else ''
        }

        return JsonResponse({
            'status': 200,
            'data': data
        }, status=200)

    def update(self, request, pk):
        """
            API update SalePromotion
        """
        sale_promotion = SalePromotion.objects.filter(pk=pk)
        if not sale_promotion:
            return JsonResponse({
                'status': 404,
                'message': 'Sale Promotion not found'
            }, status=404)

        image = request.FILES['image_file'] if 'image_file' in request.FILES else None
        sub_image = request.FILES['sub_image_file'] if 'sub_image_file' in request.FILES else None
        status = request.POST.get('status', None)
        tentcard_ctkm = request.POST.get('tentcard', None)
        wobbler_ctkm = request.POST.get('wobbler', None)

        if status is None or not (isinstance(type, int) and 0 <= type <= 3):
            return JsonResponse({
                'status': 400,
                'message': 'Invalid body (status Invalid)'
            }, status=400)

        tentcard_ctkm = True if tentcard_ctkm is not None and tentcard_ctkm == 'true' else False
        wobbler_ctkm = True if wobbler_ctkm is not None and wobbler_ctkm == 'true' else False

        fs = FileSystemStorage(
            location=settings.FS_IMAGE_UPLOADS + datetime.date.today().isoformat(),
            base_url=settings.FS_IMAGE_URL + datetime.date.today().isoformat()
        )

        if image is not None and image != '':
            image_filename = fs.save(image.name, image)
            image_url = fs.url(image_filename)
            sale_promotion.image = image_url

        elif status != 0 and (sale_promotion.image is None or sale_promotion.image == ''):
            return JsonResponse({
                'status': 400,
                'message': 'Cần upload ảnh nghiệm thu với trạng thái hiện tại của shop'
            }, status=400)

        if sub_image is not None and sub_image != '':
            sub_image_filename = fs.save(sub_image.name, sub_image)
            sub_image_url = fs.url(sub_image_filename)
            sale_promotion.sub_image = sub_image_url

        sale_promotion.status = status
        sale_promotion.tentcard_ctkm = tentcard_ctkm
        sale_promotion.wobbler_ctkm = wobbler_ctkm

        sale_promotion.save()
        return JsonResponse({
            'status': 200,
            'data': 'success'
        }, status=200)


@api_view(['POST'])
@login_required
def import_view(request):
    """
        API import SalePromotion
    """
    dataset = Dataset()

    title_id = request.POST.get('title_id', None)
    title_code = request.POST.get('title_code', None)
    title_description = request.POST.get('title_description', None)

    promotion_file = request.FILES['promotion_file']

    is_submit = request.POST.get('is_submit', None)
    is_submit = True if is_submit == 'true' else False

    if title_id is not None and title_id != '':
        promotion_title = SalePromotionTitle.objects.filter(pk=title_id).first()
        if promotion_title is None:
            return JsonResponse({
                'status': 404,
                'message': 'Invalid body (PromotionTitle not found)'
            }, status=404)
    else:
        if title_code is None or title_code == '':
            return JsonResponse({
                'status': 400,
                'message': 'Invalid body (new title_code invalid)'
            }, status=400)
        promotion_title = SalePromotionTitle.objects.filter(code__iexact=title_code).first()
        if promotion_title is not None:
            return JsonResponse({
                'status': 400,
                'message': 'Invalid body (title_code be used by other PromotionTitle)'
            }, status=400)
        promotion_title = SalePromotionTitle(
            code=title_code,
            description=title_description
        )
        if is_submit:
            promotion_title.save()

    promotion_rows = dataset.load(promotion_file.read())

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
        result = import_view_update_action(data, is_submit, promotion_title)
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

    return JsonResponse({
        'status': 200,
        'data': {
            'total_row': total_row,
            'row_create': row_create,
            'row_no_change': row_no_change,
            'row_update': row_update,
            'row_error': row_error,
            'path_data_error': render_excel_import_error(request.user, data_error)
        }
    }, status=200)


def import_view_update_action(data, is_submit=False, promotion_title=None):
    if data['terminal_id'] is None or str(data['terminal_id']) == '':
        return 'Terminal_ID: Terminal_ID trống - Lỗi dữ liệu'
    if data['shop_code'] is None or str(data['shop_code']) == '':
        return 'shop_code: shop_code trống - Lỗi dữ liệu'
    if data['staff_email'] is None or str(data['staff_email']) == '':
        return 'Sale: Sale trống - Lỗi dữ liệu'
    terminal = Terminal.objects.filter(terminal_id=data['terminal_id'])
    if not terminal:
        return 'Terminal_ID: Không tìm thấy Terminal'
    shop = Shop.objects.filter(code=data['shop_code'])
    if not shop:
        return 'shop_code: Không tìm thấy Shop'
    if terminal.shop is not shop:
        return 'Terminal-Shop: Terminal không được gán với Shop'
    staff = Staff.objects.filter(email=data['staff_email'])
    if not staff:
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
                contact_person=str(data['contact_person']),
                contact_phone_number=str(data['contact_phone_number']),
                contact_email=str(data['contact_email']),

                tentcard_ctkm=False,
                wobbler_ctkm=False,
                status=0
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
            promotion.contact_person = str(data['contact_person'])
            promotion.contact_phone_number = str(data['contact_phone_number'])
            promotion.contact_email = str(data['contact_email'])
            promotion.save()
        return message


@api_view(['GET'])
@login_required
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

    data = [{'id': title.id, 'content': title.code + ' - ' + title.description} for title in queryset]

    return JsonResponse({
        'status': 200,
        'data': data
    }, status=200)


@api_view(['DELETE'])
@login_required
def reset_data(request):
    """
        API delete all SalePromotion
    """
    SalePromotion.objects.all().delete()

    return JsonResponse({
        'status': 200,
        'data': 'Reset dữ liệu triển khai CTKM thành công!'
    }, status=200)


def render_excel_import_error(staff_email='', data=[]):

    folder_name = 'sale-promotion-import-error'
    file_name = str(staff_email) + '_' + str(int(time.time())) + '.xlsx'
    sheet_name = 'DANH SÁCH BẢN GHI LỖI'

    column_headers = ['Terminal_ID', 'Shop_code', 'Sale', 'Người lien hệ', 'SĐT liên hệ', 'Email liên hệ']

    return create_simple_excel_file(folder_name, file_name, sheet_name, column_headers, data)