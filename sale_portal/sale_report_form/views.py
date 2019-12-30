import json
import os
import time
from datetime import date
from datetime import datetime as dt_datetime

import datetime

import xlsxwriter
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view

from sale_portal import settings
from sale_portal.sale_report_form import SaleReportFormPurposeTypes
from sale_portal.sale_report_form.serializers import SaleReportStatisticSerializer
from sale_portal.shop.models import Shop
from sale_portal.user.models import User
from sale_portal.staff.models import Staff
from sale_portal.user.views import get_user_info
from sale_portal.utils import field_validator
from sale_portal.sale_report_form.models import SaleReport
from sale_portal.utils.excel_util import check_or_create_excel_folder
from sale_portal.utils.field_formatter import format_string
from sale_portal.sale_report_form.serializers import SaleReportSerializer


class SaleReportViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = SaleReportSerializer

    def get_queryset(self):
        """
            API get list SaleReport   \n
            filter theo các param purpose,shop_id ,user,team_id,from_date,to_date \n
            Có thể bỏ trống
        """
        purpose = self.request.query_params.get('purpose', None)
        shop_id = self.request.query_params.get('shop_id', None)
        user = self.request.query_params.get('user', None)
        team_id = self.request.query_params.get('team_id', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        queryset = SaleReport.objects.filter(is_draft=False)

        if purpose is not None and purpose != '':
            queryset = queryset.filter(purpose=purpose)

        if shop_id is not None and shop_id != '':
            shop_id = format_string(shop_id)
            queryset = queryset.filter(shop_code=shop_id)

        if user is not None and user != '':
            user = format_string(user)
            users = User.objects.filter(email__icontains=user)
            queryset = queryset.filter(created_by__in=users)

        if team_id is not None and team_id != '':
            staffs = Staff.objects.all().filter(team_id=team_id)
            staff_emails = [x.email for x in staffs]
            users = User.objects.filter(email__in=staff_emails)
            queryset = queryset.filter(created_by__in=users)

        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                created_date__gte=dt_datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))

        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                created_date__lte=(dt_datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

        return queryset

    def create(self, request):
        """
            API create SaleReport   \n

            HelpText - (* là bắt buộc) code - dataType - List giá trị (là {} nếu không có) - Ví dụ   \n

            Các trường bắt buộc cho tất cả loại báo cáo   \n
                Mục đích - *purpose - string(10) - ['0': 'Mở mới', '1': 'Triển khai', '2': 'Chăm sóc'] - purpose: '0'  \n
                LON - *longitude - float - {} - longitude: 105.8226176   \n
                LAT - *latitude - float - {} - latitude :101.5656   \n
                Bản nháp hay chính thức - *is_draft - boolean - {} - is_draft: true   \n

            Nếu đang tạo báo cáo trên bản nháp đã có thì cần truyền id bản nháp lên   \n
                ID bản nháp - current_draft_id - int - {} - current_draft_id: 10   \n

            Các trường cho báo cáo mở mới   \n
                Tên merchant - *new_merchant_name - string(255) - {} - new_merchant_name: 'HotPot Story'   \n
                Thương hiệu - new_merchant_brand - string(255) - {} - new_merchant_brand: 'RedSun'    \n
                Địa chỉ - new_address - text - {} - new_address: '36 Hoàng Cầu'   \n
                Tên người liên hệ - new_customer_name - string(255) - {} - new_customer_name: 'Nguyễn Thị Thùy'   \n
                SĐT liên hệ - new_phone - string(100) - {} - new_phone: '012345678'   \n
                Kết quả mở mới - *new_result - int - [0: 'Dong y, da ky duoc HD', 1: 'Dong y, chua ky duoc HD', 2: 'Can xem xet them', 3: 'Tu choi hop tac'] - new_result: 0   \n
                MC đang sử dụng PM bán hàng - new_using_application - string(100) - ['iPos', 'Sapo', 'KiotViet', 'POS365', 'Cukcuk', 'Ocha', 'PM khác', 'Chưa sử dụng'] - new_using_application: 'iPos'   \n
                Ghi chú - new_note - text - {} - new_note: 'Đây là ghi chú test xxxx'   \n

            Các trường dùng chung cho báo cáo triển khai & chăm sóc   \n
                Cửa hàng - *shop_id - int - {} - shop_id: 47215  \n
                HA nghiệm thu (Ngoài CH) - *image_outside - binary - {} - image_outside: (binary)   \n
                HA nghiệm thu (Trong CH) - *image_inside - binary - {} - image_inside: (binary)   \n
                HA nghiệm thu (Quầy thu ngân) - *image_store_cashier - binary - {} - image_store_cashier: (binary)   \n
                Bộ posm triển khai bao gồm - standeeQr - int - {} - standeeQr: 2   \n
                Bộ posm triển khai bao gồm - stickerTable - int - {} - stickerTable: 2   \n
                Bộ posm triển khai bao gồm - wobbler - int - {} - wobbler: 2   \n
                Bộ posm triển khai bao gồm - standeeCtkm - int - {} - standeeCtkm: 2   \n
                Bộ posm triển khai bao gồm - stickerDoor - int - {} - stickerDoor: 2   \n
                Bộ posm triển khai bao gồm - guide - int - {} - guide: 2   \n
                Bộ posm triển khai bao gồm - poster - int - {} - poster: 2   \n
                Bộ posm triển khai bao gồm - tentcard - int - {} - tentcard: 2   \n

            Các trường cho tạo báo cáo triển khai   \n
                Xác thực shop - *implement_confirm - int - [0, 1, 2] - implement_confirm: 1   \n
                Merchant view cho Terminal gồm - *implement_merchant_view - array() - [1: 'web', 2: 'app', 3: 'other'] - implement_merchant_view: [2, 3]   \n
                Đã hướng dẫn nghiệp vụ cho - *implement_career_guideline - array() - [0: 'Thu ngân', 1: 'Cửa hàng trưởng'] - implement_career_guideline: [0, 1]   \n
            Nếu Triển khai - implement_confirm = 1 thì nhập thêm trường   \n
                Địa chỉ mới - *implement_new_address - text - {} - implement_new_address: '34 Phùng Hưng'   \n

            Các trường cho tạo báo cáo chăm sóc   \n
                Tình trạng cửa hàng - *shop_status - int - [0: 'Da nghi kinh doanh/ khong co cua hang thuc te', 1: 'Muon thanh ly QR', 2: 'Dang hoat dong', 3: 'Không hợp tác', 4: 'Da chuyen dia diem'] - shop_status: 2  \n
            Nếu shop_status <> 2 không upload 3 ảnh nhưng thêm 2 trường sau  \n
                Mô tả - *cessation_of_business_note - text - {} - cessation_of_business_note: 'Không tìm được cửa hàng để chăm sóc'   \n
                Ảnh nghiệm thu - *cessation_of_business_image - binary - {} - cessation_of_business_image: (binary)   \n
            Nếu shop_status = 2 cần upload 3 ảnh & thêm các trường dưới  \n
                Ký HĐ thưởng thu ngân không - *customer_care_cashier_reward - int - [0: 'Không', 1: 'Có'] - customer_care_cashier_reward: 0   \n
                Số giao dịch phát sinh trong thời gian chăm sóc - *customer_care_transaction - int - {} - customer_care_transaction: 4   \n

            Chú ý: nếu là bản nháp ko cần upload ảnh - Không push ảnh lên server   \n

        """

        # Data nhận dưới dạng form data, sau đó convert ra json rồi xử lý
        data = request.POST.get('data', None)
        datajson = json.loads(data)

        purpose = datajson.get('purpose')
        longitude = datajson.get('longitude')
        latitude = datajson.get('latitude')
        is_draft = datajson.get('is_draft')
        current_draft_id = datajson.get('current_draft_id')
        # validate purpose, longitude, latitude, is_draft
        if purpose is None \
                or longitude is None or longitude == '0' \
                or latitude is None or latitude == '0' \
                or is_draft is None:
            return self.response(
                status=400, message='Validate error: purpose, longitude, latitude, is_draft are required')

        purpose = format_string(purpose, True)
        if purpose not in ['0', '1', '2']:
            return self.response(status=400, message='Validate error: Purpose is incorrect')

        # Create or find sale_report object if has a draft version
        if str(is_draft).lower() == 'true':
            is_draft = True
        else:
            is_draft = False

        sale_report = None
        if current_draft_id is not None:
            sale_report = get_object_or_404(SaleReport, pk=current_draft_id, is_draft=True)

        if sale_report is None:
            sale_report = SaleReport()
        elif sale_report.created_date.date() != date.today():
            return self.response(status=400, message='Only allow access to drafts created on today')

        # Xu ly request Mở Mới
        if purpose == '0':
            new_merchant_name = datajson.get('new_merchant_name')
            new_merchant_brand = datajson.get('new_merchant_brand')
            new_address = datajson.get('new_address')
            new_customer_name = datajson.get('new_customer_name')
            new_phone = datajson.get('new_phone')
            new_result = datajson.get('new_result')
            new_note = datajson.get('new_note')
            new_using_application = datajson.get('new_using_software')

            try:
                field_validator.validate_merchant_name(
                    format_string(new_merchant_name), allow_none=False, allow_blank=False, rase_exception=True)
                field_validator.validate_merchant_brand(
                    format_string(new_merchant_brand), allow_none=True, allow_blank=True, rase_exception=True)
                field_validator.validate_address(
                    format_string(new_address), allow_none=True, allow_blank=True, rase_exception=True)
                field_validator.validate_customer_name(
                    format_string(new_customer_name), allow_none=True, allow_blank=True, rase_exception=True)
                field_validator.validate_phone(
                    format_string(new_phone), allow_none=True, allow_blank=True, rase_exception=True)
                field_validator.validate_note(
                    format_string(new_note), allow_none=True, allow_blank=True, rase_exception=True)
                field_validator.validate_in_string_list([
                    'iPos',
                    'Sapo',
                    'KiotViet',
                    'POS365',
                    'Cukcuk',
                    'Ocha',
                    'PM khác',
                    'Chưa sử dụng'
                ], 'new_using_application', format_string(new_using_application), True, True, True)

                sale_report.new_merchant_name = format_string(new_merchant_name, True)
                sale_report.new_merchant_brand = format_string(new_merchant_brand, True)
                sale_report.new_address = format_string(new_address, True)
                sale_report.new_customer_name = format_string(new_customer_name, True)
                sale_report.new_phone = format_string(new_phone, True)
                sale_report.new_result = new_result
                sale_report.new_note = format_string(new_note, True)
                sale_report.new_using_application = format_string(new_using_application, True)
            except Exception as e:
                return JsonResponse({
                    'status': 400,
                    'message': 'Validate error: ' + str(e),
                }, status=400)

        # Xu ly request Triển khai
        elif purpose == '1':
            shop_id = datajson.get('shop_id')
            image_outside_v2 = datajson.get('image_outside')
            image_inside_v2 = datajson.get('image_inside')
            image_store_cashier_v2 = datajson.get('image_store_cashier')
            implement_merchant_view = datajson.get('implement_merchant_view')
            implement_career_guideline = datajson.get('implement_career_guideline')
            implement_confirm = datajson.get('implement_confirm')
            implement_new_address = datajson.get('new_address_input')

            standeeQr = datajson.get('standeeQr')
            stickerTable = datajson.get('stickerTable')
            wobbler = datajson.get('wobbler')
            standeeCtkm = datajson.get('standeeCtkm')
            stickerDoor = datajson.get('stickerDoor')
            guide = datajson.get('guide')
            poster = datajson.get('poster')
            tentcard = datajson.get('tentcard')

            shop = get_object_or_404(Shop, pk=shop_id)
            sale_report.shop_code = shop.code

            try:
                field_validator.validate_in_string_list([0, 1, 2], \
                                                        'implement_confirm', implement_confirm, False, False, True)
                if implement_merchant_view is None:
                    raise Exception('implement_merchant_view is required')
                sale_report.implement_merchant_view = format_string(implement_merchant_view, True)
                sale_report.implement_career_guideline = format_string(implement_career_guideline, True)
                sale_report.implement_confirm = format_string(implement_confirm, True)
                posm_v2 = {}
                field_validator.validate_posm_field(name='standeeQr', input=standeeQr)
                field_validator.validate_posm_field(name='stickerTable', input=stickerTable)
                field_validator.validate_posm_field(name='wobbler', input=wobbler)
                field_validator.validate_posm_field(name='standeeCtkm', input=standeeCtkm)
                field_validator.validate_posm_field(name='stickerDoor', input=stickerDoor)
                field_validator.validate_posm_field(name='guide', input=guide)
                field_validator.validate_posm_field(name='poster', input=poster)
                field_validator.validate_posm_field(name='tentcard', input=tentcard)
                posm_v2.update({
                    'standeeQr': standeeQr,
                    'stickerTable': stickerTable,
                    'wobbler': wobbler,
                    'standeeCtkm': standeeCtkm,
                    'stickerDoor': stickerDoor,
                    'guide': guide,
                    'poster': poster,
                    'tentcard': tentcard,
                })
                sale_report.posm_v2 = json.dumps(posm_v2)
                if implement_confirm == '1':
                    field_validator.validate_address(format_string(implement_new_address), False, False, True)
                    sale_report.implement_new_address = format_string(implement_new_address, True)
            except Exception as e:
                return self.response(status=400, message='Validate error: ' + str(e))

            # save image
            if not is_draft:
                if image_outside_v2 is None or image_outside_v2 == '' \
                        or image_inside_v2 is None or image_inside_v2 == '' \
                        or image_store_cashier_v2 is None or image_store_cashier_v2 == '':

                    return self.response(
                        status=400,
                        message='Validate error: image_outside, image_inside, image_store_cashier are required'
                    )
                else:
                    sale_report.image_outside_v2 = format_string(image_outside_v2, True)
                    sale_report.image_inside_v2 = format_string(image_inside_v2, True)
                    sale_report.image_store_cashier_v2 = format_string(image_store_cashier_v2, True)

        # Xu ly request Chăm sóc
        else:
            shop_id = datajson.get('shop_id')
            shop_status = datajson.get('shop_status')
            image_outside = datajson.get('image_outside')
            image_inside = datajson.get('image_inside')
            image_store_cashier = datajson.get('image_store_cashier')

            standeeQr = datajson.get('standeeQr')
            stickerTable = datajson.get('stickerTable')
            wobbler = datajson.get('wobbler')
            standeeCtkm = datajson.get('standeeCtkm')
            stickerDoor = datajson.get('stickerDoor')
            guide = datajson.get('guide')
            poster = datajson.get('poster')
            tentcard = datajson.get('tentcard')

            cessation_of_business_note = datajson.get('cessation_of_business_note')
            cessation_of_business_image_v2 = datajson.get('cessation_of_business_image')

            customer_care_cashier_reward = datajson.get('cashier_reward')
            customer_care_transaction = datajson.get('transaction')

            shop = get_object_or_404(Shop, pk=shop_id)
            sale_report.shop_code = shop.code

            try:
                field_validator.validate_in_string_list(
                    ['0', '1', '2', '3', '4'], 'shop_status', format_string(str(shop_status)), False, False, True)
                sale_report.shop_status = int(shop_status)
                if sale_report.shop_status == 2:
                    field_validator.validate_in_string_list(
                        ['0', '1'],
                        'customer_care_cashier_reward',
                        format_string(str(customer_care_cashier_reward)), False, False, True)
                    field_validator.validate_transaction(format_string(customer_care_transaction), False, False, True)
                    sale_report.customer_care_cashier_reward = format_string(customer_care_cashier_reward, True)
                    sale_report.customer_care_transaction = format_string(customer_care_transaction, True)
                    posm_v2 = {}
                    field_validator.validate_posm_field(name='standeeQr', input=standeeQr)
                    field_validator.validate_posm_field(name='stickerTable', input=stickerTable)
                    field_validator.validate_posm_field(name='wobbler', input=wobbler)
                    field_validator.validate_posm_field(name='standeeCtkm', input=standeeCtkm)
                    field_validator.validate_posm_field(name='stickerDoor', input=stickerDoor)
                    field_validator.validate_posm_field(name='guide', input=guide)
                    field_validator.validate_posm_field(name='poster', input=poster)
                    field_validator.validate_posm_field(name='tentcard', input=tentcard)
                    posm_v2.update({
                        'standeeQr': standeeQr,
                        'stickerTable': stickerTable,
                        'wobbler': wobbler,
                        'standeeCtkm': standeeCtkm,
                        'stickerDoor': stickerDoor,
                        'guide': guide,
                        'poster': poster,
                        'tentcard': tentcard,
                    })
                    sale_report.posm_v2 = json.dumps(posm_v2)
                else:
                    field_validator.validate_note(format_string(cessation_of_business_note), False, False, True)
                    sale_report.cessation_of_business_note = format_string(cessation_of_business_note, True)
            except Exception as e:
                return self.response(status=400, message='Validate error: ' + str(e))

            # save image
            if not is_draft and shop_status == 2:
                if image_outside is None or image_outside == '' \
                        or image_inside is None or image_inside == '' \
                        or image_store_cashier is None or image_store_cashier == '':
                    return self.response(
                        status=400, message='image_outside, image_inside, image_store_cashier are required')
                sale_report.image_outside_v2 = image_outside
                sale_report.image_inside_v2 = image_inside
                sale_report.image_store_cashier_v2 = image_store_cashier

            if not is_draft and shop_status != 2:
                if cessation_of_business_image_v2 is None or cessation_of_business_image_v2 == '':
                    return self.response(
                        status=400, message='cessation_of_business_image is required')

                sale_report.cessation_of_business_image_v2 = cessation_of_business_image_v2

        sale_report.purpose = purpose
        sale_report.longitude = float(longitude)
        sale_report.latitude = float(latitude)
        sale_report.created_by = request.user
        sale_report.updated_by = request.user
        sale_report.is_draft = is_draft

        try:
            sale_report.save()
        except Exception as e:
            return self.response(
                status=400, message='Save sale_report_form error: ' + str(e))

        return self.response(status=200, message='Created')

    def retrieve(self, request, pk):
        """
            API get detail Sale_report
        """
        sale_report = get_object_or_404(SaleReport, pk=pk)
        if sale_report.shop_code is not None and sale_report.shop_code != '':
            shop = get_object_or_404(Shop, code=sale_report.shop_code)

        if sale_report.data_version == 1:
            image_outside = sale_report.image_outside.url if sale_report.image_outside else ''
            image_inside = sale_report.image_inside.url if sale_report.image_inside else ''
            image_store_cashier = sale_report.image_store_cashier.url if sale_report.image_store_cashier else ''
            posm = ''
        else:
            image_outside = sale_report.image_outside_v2
            image_inside = sale_report.image_inside_v2
            image_store_cashier = sale_report.image_store_cashier_v2
            posm = sale_report.posm_v2

        data = {
            'purpose': sale_report.purpose,
            'longitude': sale_report.longitude,
            'latitude': sale_report.latitude,
            'sale': {
                'email': sale_report.created_by.email
            },
            'new': {
                'new_merchant_name': sale_report.new_merchant_name,
                'new_merchant_brand': sale_report.new_merchant_brand,
                'new_address': sale_report.new_address,
                'new_customer_name': sale_report.new_customer_name,
                'new_phone': sale_report.new_phone,
                'new_result': sale_report.new_result,
                'new_using_application': sale_report.new_using_application,
                'new_note': sale_report.new_note
            },
            'shop': {
                'shop_id': shop.id if sale_report.shop_code else 0,
                'shop_address': shop.address if sale_report.shop_code else '',
                'shop_code': sale_report.shop_code if sale_report.shop_code else '',
                'shop_name': shop.name if sale_report.shop_code else ''
            },
            'shop_status': sale_report.shop_status,
            'image_outside': image_outside,
            'image_inside': image_inside,
            'image_store_cashier': image_store_cashier,
            'posm': posm,

            # nghỉ kinh doanh
            'cessation_of_business_note': sale_report.cessation_of_business_note,
            'cessation_of_business_image': sale_report.cessation_of_business_image.url if sale_report.cessation_of_business_image else '',

            # chăm sóc
            'customer_care_cashier_reward': sale_report.customer_care_cashier_reward,
            'customer_care_transaction': sale_report.customer_care_transaction,

            # triển khai
            'implement_merchant_view': sale_report.implement_merchant_view,
            'implement_career_guideline': sale_report.implement_career_guideline,
            'implement_confirm': sale_report.implement_confirm,
            'implement_new_address': sale_report.implement_new_address
        }

        return JsonResponse({
            'status': 200,
            'data': data
        })

    def response(self, status, message):
        return JsonResponse({
            'status': int(status),
            'message': str(message),
        }, status=int(status))


class SaleReportStatisticViewSet(mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    serializer_class = SaleReportStatisticSerializer

    def get_queryset(self):
        """
            API get SaleReportStatisticView   \n
            param có report_date report_month team_id
        """
        report_date = self.request.query_params.get('date', None)
        report_month = self.request.query_params.get('month', None)
        team_id = self.request.query_params.get('team_id', None)
        raw_query = get_raw_query_statistic(user=self.request.user, report_date=report_date, report_month=report_month,
                                            team_id=team_id)
        queryset = SaleReport.objects.raw(raw_query)
        return queryset


def get_raw_query_statistic(user=None, report_date=None, report_month=None, team_id=None):
    filter_time = ''
    if report_month is not None and report_month != '':
        filter_time += "and to_char(created_date, 'MM-YYYY') = '" + report_month + "'"
    else:
        if report_date is None or report_date == '':
            report_date = datetime.date.today()
        filter_time += "and created_date :: date = '" + str(report_date) + "'"

    user = get_user_info(user)  # for filter by permission
    if team_id is not None:
        staffs = Staff.objects.all().filter(team_id=team_id)
        staff_emails = [x.email for x in staffs]
        users = User.objects.filter(email__in=staff_emails)
        users_id = [x.id for x in users]
        filter_user = 'and created_by_id in {}'.format(tuple(users_id))
        if filter_user.endswith(",)"):
            filter_user = filter_user[:-2] + ")"
        elif filter_user.endswith(", )"):
            filter_user = filter_user[:-3] + ")"
    else:
        filter_user = 'and created_by_id is not null'

    raw_query = '''
        SELECT au.username,
               au.email, 
               Concat(au.last_name, ' ', au.first_name) AS full_name,
               data_statistic.* 
        FROM   auth_user au 
               INNER JOIN (SELECT created_by_id AS id, 
                                  Count(*)      AS count_total, 
                                  Count(CASE 
                                          WHEN purpose = 0 THEN 1 
                                          ELSE NULL 
                                        END)    AS count_new, 
                                  Count(CASE 
                                          WHEN purpose = 1 THEN 1 
                                          ELSE NULL 
                                        END)    AS count_impl, 
                                  Count(CASE 
                                          WHEN purpose = 2 THEN 1 
                                          ELSE NULL 
                                        END)    AS count_care, 
                                  Count(CASE 
                                          WHEN purpose = 0 
                                               AND new_result = 0 THEN 1 
                                         ELSE NULL 
                                       END)    AS count_new_signed, 
                                 Count(CASE 
                                          WHEN purpose = 0 
                                               AND new_result = 1 THEN 1 
                                          ELSE NULL 
                                        END)    AS count_new_unsigned, 
                                  Count(CASE 
                                          WHEN purpose = 0 
                                               AND new_result = 2 THEN 1 
                                          ELSE NULL 
                                        END)    AS count_new_consider, 
                                  Count(CASE 
                                          WHEN purpose = 0 
                                               AND new_result = 3 THEN 1 
                                          ELSE NULL 
                                        END)    AS count_new_refused, 
                                  Count(CASE 
                                          WHEN purpose = 2 
                                              AND shop_status = 0 THEN 1 
                                          ELSE NULL 
                                       END)    AS count_care_cessation, 
                                 Count(CASE 
                                         WHEN purpose = 2 
                                              AND shop_status = 1 THEN 1 
                                         ELSE NULL 
                                       END)    AS count_care_liquidation, 
                                  Count(CASE 
                                          WHEN purpose = 2 
                                               AND shop_status = 2 THEN 1 
                                          ELSE NULL 
                                        END)    AS count_care_opening, 
                                 Count(CASE 
                                          WHEN purpose = 2 
                                              AND shop_status = 3 THEN 1 
                                          ELSE NULL 
                                        END)    AS count_care_uncooperative ,
                                 Sum(CASE WHEN
                                            is_json(posm_v2) and posm_v2 :: json ->> 'standeeQr' is not null and
                                            posm_v2 :: json ->> 'standeeQr' ~ E'^\\\d+$' and purpose != 0
                                        THEN
                                            CAST(posm_v2 :: json ->> 'standeeQr' as Integer)
                                        ELSE 0
                                    END)       AS count_standee_qr,
                                 Sum(CASE WHEN
                                            is_json(posm_v2) and posm_v2 :: json ->> 'stickerDoor' is not null and
                                            posm_v2 :: json ->> 'stickerDoor' ~ E'^\\\d+$' and purpose != 0
                                        THEN
                                            CAST(posm_v2 :: json ->> 'stickerDoor' as Integer)
                                        ELSE 0
                                    END)       AS count_sticker_door,
                                 Sum(CASE WHEN
                                            is_json(posm_v2) and posm_v2 :: json ->> 'stickerTable' is not null and
                                            posm_v2 :: json ->> 'stickerTable' ~ E'^\\\d+$' and purpose != 0
                                        THEN
                                            CAST(posm_v2 :: json ->> 'stickerTable' as Integer)
                                        ELSE 0
                                    END)       AS count_sticker_table,
                                 Sum(CASE WHEN
                                            is_json(posm_v2) and posm_v2 :: json ->> 'guide' is not null and
                                            posm_v2 :: json ->> 'guide' ~ E'^\\\d+$' and purpose != 0
                                        THEN
                                            CAST(posm_v2 :: json ->> 'guide' as Integer)
                                        ELSE 0
                                    END)       AS count_guide,
                                 Sum(CASE WHEN
                                            is_json(posm_v2) and posm_v2 :: json ->> 'wobbler' is not null and
                                            posm_v2 :: json ->> 'wobbler' ~ E'^\\\d+$' and purpose != 0
                                        THEN
                                            CAST(posm_v2 :: json ->> 'wobbler' as Integer)
                                        ELSE 0
                                    END)       AS count_wobbler,
                                   Sum(CASE WHEN
                                            is_json(posm_v2) and posm_v2 :: json ->> 'poster' is not null and
                                            posm_v2 :: json ->> 'poster' ~ E'^\\\d+$' and purpose != 0
                                        THEN
                                            CAST(posm_v2 :: json ->> 'poster' as Integer)
                                        ELSE 0
                                    END)       AS count_poster,
                                 Sum(CASE WHEN
                                            is_json(posm_v2) and posm_v2 :: json ->> 'standeeCtkm' is not null and
                                            posm_v2 :: json ->> 'standeeCtkm' ~ E'^\\\d+$' and purpose != 0
                                        THEN
                                            CAST(posm_v2 :: json ->> 'standeeCtkm' as Integer)
                                        ELSE 0
                                    END)       AS count_standee_ctkm,
                                 Sum(CASE WHEN
                                            is_json(posm_v2) and posm_v2 :: json ->> 'tentcard' is not null and
                                            posm_v2 :: json ->> 'tentcard' ~ E'^\\\d+$' and purpose != 0
                                        THEN
                                            CAST(posm_v2 :: json ->> 'tentcard' as Integer)
                                        ELSE 0
                                    END)       AS count_tentcard                                                                                                                                                  
                          FROM   sale_report_form 
                          WHERE  is_draft = false %s %s
                          GROUP  BY created_by_id) AS data_statistic 
                      ON data_statistic.id = au.id; 
    ''' % (filter_time, filter_user)
    return raw_query


@api_view(['GET'])
@login_required
def list_draff(request):
    """
        API get list_draff   \n
        trả về danh sách tên các bản nháp \n
        param có name , là chuỗi ký tự để search
    """
    queryset = SaleReport.objects.values('id', 'purpose', 'new_merchant_brand', 'shop_code')
    queryset = queryset.filter(created_by=request.user)
    queryset = queryset.filter(is_draft=True)
    today_min = dt_datetime.combine(date.today(), time.min)
    today_max = dt_datetime.combine(date.today(), time.max)
    queryset = queryset.filter(created_date__range=(today_min, today_max))

    name = request.GET.get('name', None)

    if name is not None and name != '':
        queryset = queryset.filter(Q(shop_code__icontains=name) | Q(new_merchant_brand__icontains=name))

    data = []
    for draft in queryset:
        purpose = SaleReportFormPurposeTypes.CHOICES[draft['purpose']][1] + ' - ';
        if draft['purpose'] == 0:
            purpose += str(draft['new_merchant_brand'])
        elif draft['shop_code']:
            purpose += str(draft['shop_code']) + ' - '
            shop = Shop.objects.filter(code=draft['shop_code']).first()
            if shop:
                purpose += shop.merchant.merchant_brand if shop.merchant else ' '
                purpose += ' - ' + str(shop.address)

        data.append({'id': draft['id'], 'purpose': purpose})

    return JsonResponse({
        'status': 200,
        'data': data
    }, status=200)


@api_view(['GET'])
@login_required
def export_excel(request):
    """
        API get export statistic view to excel   \n
        trả về danh sách tên các bản nháp \n
    """
    check_or_create_excel_folder()

    if not os.path.exists(settings.MEDIA_ROOT + '/excel/sale-report-statistic'):
        os.mkdir(os.path.join(settings.MEDIA_ROOT + '/excel', 'sale-report-statistic'))

    file_name = 'sale_report_statistic_' + str(int(time.time())) + '.xlsx'
    workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + '/excel/sale-report-statistic/' + file_name)
    worksheet = workbook.add_worksheet('THỐNG KÊ HOẠT ĐỘNG SALE')

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
    worksheet.merge_range('A1:A2', 'Nhân viên', merge_format)
    worksheet.merge_range('B1:B2', 'Email', merge_format)
    worksheet.merge_range('C1:F1', 'Nhân viên', merge_format)
    worksheet.merge_range('C1:F1', 'Tổng số lần tiếp xúc', merge_format)
    worksheet.merge_range('G1:J1', 'Kết quả mở mới', merge_format)
    worksheet.merge_range('K1:N1', 'Kết quả chăm sóc', merge_format)
    worksheet.merge_range('O1:V1', 'Số lượng ấn phẩm sử dụng', merge_format)
    worksheet.write('C2', 'Tổng', merge_format)
    worksheet.write('D2', 'Số MC chăm sóc', merge_format)
    worksheet.write('E2', 'Số MC triển khai', merge_format)
    worksheet.write('F2', 'Số MC tiếp cận mở mới', merge_format)
    worksheet.write('G2', 'Đồng ý, đã kí hợp đồng', merge_format)
    worksheet.write('H2', 'Đồng ý, chưa kí hợp đồng', merge_format)
    worksheet.write('I2', 'Cần xem xét', merge_format)
    worksheet.write('J2', 'Từ chối hợp tác', merge_format)
    worksheet.write('K2', 'Đã nghỉ kinh doanh', merge_format)
    worksheet.write('L2', 'Muốn thanh lý QR', merge_format)
    worksheet.write('M2', 'Đang hoạt động', merge_format)
    worksheet.write('N2', 'Không hợp tác', merge_format)
    worksheet.write('O2', 'StandeeQR', merge_format)
    worksheet.write('P2', 'Sticker dán cửa', merge_format)
    worksheet.write('Q2', 'Sticker dán bàn thu ngân', merge_format)
    worksheet.write('R2', 'Hướng dẫn sử dụng', merge_format)
    worksheet.write('S2', 'Wobbler CTKM', merge_format)
    worksheet.write('T2', 'Poster CTKM', merge_format)
    worksheet.write('U2', 'Standee CTKM(60x160)', merge_format)
    worksheet.write('V2', 'Tentcard CTKM', merge_format)
    worksheet.freeze_panes(2, 0)

    data = get_statistic_data(request)

    row_num = 2
    for item in data:
        worksheet.write(row_num, 0, item.full_name)
        worksheet.write(row_num, 1, item.email)
        worksheet.write(row_num, 2, item.count_total)
        worksheet.write(row_num, 3, item.count_new)
        worksheet.write(row_num, 4, item.count_impl)
        worksheet.write(row_num, 5, item.count_care)
        worksheet.write(row_num, 6, item.count_new_signed)
        worksheet.write(row_num, 7, item.count_new_unsigned)
        worksheet.write(row_num, 8, item.count_new_consider)
        worksheet.write(row_num, 9, item.count_new_refused)
        worksheet.write(row_num, 10, item.count_care_cessation)
        worksheet.write(row_num, 11, item.count_care_liquidation)
        worksheet.write(row_num, 12, item.count_care_opening)
        worksheet.write(row_num, 13, item.count_care_uncooperative)
        worksheet.write(row_num, 14, item.count_standee_qr)
        worksheet.write(row_num, 15, item.count_sticker_door)
        worksheet.write(row_num, 16, item.count_sticker_table)
        worksheet.write(row_num, 17, item.count_guide)
        worksheet.write(row_num, 18, item.count_wobbler)
        worksheet.write(row_num, 19, item.count_poster)
        worksheet.write(row_num, 20, item.count_standee_ctkm)
        worksheet.write(row_num, 21, item.count_tentcard)

        row_num += 1

    workbook.close()

    return JsonResponse({
        'status': 200,
        'data': settings.MEDIA_URL + '/excel/sale-report-statistic/' + file_name},
        status=200
    )


def get_statistic_data(request):
    report_date = request.GET.get('date', None)
    report_month = request.GET.get('month', None)
    team_id = request.GET.get('team_id', None)

    raw_query = get_raw_query_statistic(request.user, report_date=report_date, report_month=report_month,
                                        team_id=team_id)

    if raw_query == '':
        return []
    else:
        return SaleReport.objects.raw(raw_query)
