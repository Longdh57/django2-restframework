import datetime
import json
import time
from datetime import date
from datetime import datetime as dt_datetime

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins

from sale_portal.sale_report_form.models import SaleReport
from sale_portal.sale_report_form.serializers import SaleReportSerializer
from sale_portal.shop.models import Shop
from sale_portal.staff.models import Staff
from sale_portal.user.models import User
from sale_portal.utils import field_validator
from sale_portal.utils.field_formatter import format_string


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

            Các trường cho tạo báo cáo triển khai   \n
                Xác thực shop - *implement_confirm - int - [0, 1, 2] - implement_confirm: 1   \n
                Bộ posm triển khai bao gồm - implement_posm - text - {} - implement_posm:[{"standeeQr":"2","stickerDoor":"4","stickerTable":"4","guide":"4","wobbler":"4","poster":"3","standeeCtkm":"4","tentcard":"4"}]   \n
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
                Bộ posm triển khai bao gồm: (note: 8 mục, bỏ cái 'Hàng 9' đi) - customer_care_posm - text - {} - customer_care_posm:[{"standeeQr":"2","stickerDoor":"4","stickerTable":"4","guide":"4","wobbler":"4","poster":"3","standeeCtkm":"4","tentcard":"4"}]   \n
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

        if purpose is None \
                or longitude is None or longitude == '0' \
                or latitude is None or latitude == '0' \
                or is_draft is None:
            return JsonResponse({
                'status': 400,
                'message': 'Some data fields such as purpose, longitude, latitude, is_draft are required',
            }, status=400)

        # Create or find sale_report object if has a draft version
        if is_draft == 'true':
            is_draft = True
        else:
            is_draft = False

        sale_report = None
        if current_draft_id is not None:
            sale_report = get_object_or_404(SaleReport, pk=current_draft_id, is_draft=True)

        if sale_report is None:
            sale_report = SaleReport()
        elif sale_report.created_date.date() != date.today():
            return JsonResponse({
                'status': 400,
                'message': 'Only allow access to drafts created on today',
            }, status=400)

        # other purpose data from request
        shop_id = datajson.get('shop_id')
        shop_status = datajson.get('shop_status')
        image_outside = request.FILES['image_outside'] if 'image_outside' in request.FILES else None
        image_inside = request.FILES['image_inside'] if 'image_inside' in request.FILES else None
        image_store_cashier = \
            request.FILES['image_shop_cashier'] if 'image_shop_cashier' in request.FILES else None

        cessation_of_business_note = datajson.get('cessation_of_business_note')
        cessation_of_business_image = request.FILES[
            'cessation_of_business_image'] if 'cessation_of_business_image' in request.FILES else None

        customer_care_posm = datajson.get('customer_care_posm')
        customer_care_cashier_reward = datajson.get('customer_care_cashier_reward')
        customer_care_transaction = datajson.get('customer_care_transaction')

        # for upload images
        fs = FileSystemStorage(
            location=settings.FS_IMAGE_UPLOADS + datetime.date.today().isoformat(),
            base_url=settings.FS_IMAGE_URL + datetime.date.today().isoformat()
        )

        # ingest data to sale_report object
        purpose = format_string(purpose, True)
        if purpose not in ['0', '1', '2']:
            return JsonResponse({
                'status': 400,
                'message': 'Purpose is incorrect',
            }, status=400)

        if purpose == '0':
            # open_new_shop purpose data from request
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

        elif purpose == '1':
            shop_id = datajson.get('shop_id')
            shop_status = datajson.get('verify_shop')
            image_outside = request.FILES['image_outside'] if 'image_outside' in request.FILES else None
            image_inside = request.FILES['image_inside'] if 'image_inside' in request.FILES else None
            image_store_cashier = \
                request.FILES['image_shop_cashier'] if 'image_shop_cashier' in request.FILES else None
            implement_posm = datajson.get('implement_posm')
            implement_merchant_view = datajson.get('implement_merchant_view')
            implement_career_guideline = datajson.get('implement_career_guideline')
            implement_confirm = datajson.get('verify_shop')
            implement_new_address = datajson.get('new_address_input')

            shop = get_object_or_404(Shop, pk=shop_id)
            sale_report.shop_code = shop.code

            try:
                field_validator.validate_in_string_list(['0', '1', '2'], \
                                                        'verify_shop', implement_confirm, False, False, True)
                if implement_merchant_view is None:
                    raise Exception('implement_merchant_view is required')
                sale_report.implement_posm = format_string(implement_posm, True)
                sale_report.implement_merchant_view = format_string(implement_merchant_view, True)
                sale_report.implement_career_guideline = format_string(implement_career_guideline, True)
                sale_report.implement_confirm = format_string(implement_confirm, True)
                if implement_confirm == '1':
                    field_validator.validate_address(format_string(implement_new_address), False, False, True)
                    sale_report.implement_new_address = format_string(implement_new_address, True)
            except Exception as e:
                return JsonResponse({
                    'status': 400,
                    'message': 'Validate error: ' + str(e),
                }, status=400)

            # save image
            if not is_draft:
                if image_outside is None or image_outside == '' \
                        or image_inside is None or image_inside == '' \
                        or image_store_cashier is None and image_store_cashier == '':
                    return JsonResponse({
                        'status': 400,
                        'message': 'image_outside, image_inside, image_store_cashier are required',
                    }, status=400)
                try:
                    pre_fix = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d__%H_%M_%S__')

                    image_outside_filename = 'image_outside__' + pre_fix + '.jpg'
                    image_outside_filename = fs.save(image_outside_filename, image_outside)
                    image_outside_url = fs.url(image_outside_filename)

                    image_inside_filename = 'image_inside__' + pre_fix + '.jpg'
                    image_inside_filename = fs.save(image_inside_filename, image_inside)
                    image_inside_url = fs.url(image_inside_filename)

                    image_store_cashier_filename = 'image_store_cashier__' + pre_fix + '.jpg'
                    image_store_cashier_filename = fs.save(image_store_cashier_filename, image_store_cashier)
                    image_store_cashier_url = fs.url(image_store_cashier_filename)

                    sale_report.image_outside = image_outside_url if image_outside_url is not None else None
                    sale_report.image_inside = image_inside_url if image_inside_url is not None else None
                    sale_report.image_store_cashier = image_store_cashier_url if image_store_cashier_url is not None else None
                except Exception as e:
                    return JsonResponse({
                        'status': 500,
                        'message': 'Save file error: ' + str(e),
                    }, status=500)

        else:
            shop = get_object_or_404(Shop, pk=shop_id)
            sale_report.shop_code = shop.code
            try:
                field_validator.validate_in_string_list(['0', '1', '2', '3', '4'], 'shop_status',
                                                        format_string(shop_status),
                                                        False,
                                                        False, True)
                sale_report.shop_status = format_string(shop_status, True)
                if sale_report.shop_status == '2':
                    field_validator.validate_in_string_list(['0', '1'], 'customer_care_cashier_reward',
                                                            format_string(customer_care_cashier_reward), False, False,
                                                            True)
                    field_validator.validate_transaction(format_string(customer_care_transaction), False, False, True)
                    sale_report.customer_care_cashier_reward = format_string(customer_care_cashier_reward, True)
                    sale_report.customer_care_transaction = format_string(customer_care_transaction, True)
                else:
                    field_validator.validate_note(format_string(cessation_of_business_note), False, False, True)
                    sale_report.cessation_of_business_note = format_string(cessation_of_business_note, True)
            except Exception as e:
                return JsonResponse({
                    'status': 400,
                    'message': 'Validate error: ' + str(e),
                }, status=400)
            # save image
            if not is_draft and shop_status == '2':
                if image_outside is None or image_outside == '' \
                        or image_inside is None or image_inside == '' \
                        or image_store_cashier is None and image_store_cashier == '':
                    return JsonResponse({
                        'status': 400,
                        'message': 'image_outside, image_inside, image_store_cashier are required',
                    }, status=400)
                try:
                    pre_fix = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d__%H_%M_%S__')

                    image_outside_filename = 'image_outside__' + pre_fix + '.jpg'
                    image_outside_filename = fs.save(image_outside_filename, image_outside)
                    image_outside_url = fs.url(image_outside_filename)

                    image_inside_filename = 'image_inside__' + pre_fix + '.jpg'
                    image_inside_filename = fs.save(image_inside_filename, image_inside)
                    image_inside_url = fs.url(image_inside_filename)

                    image_store_cashier_filename = 'image_store_cashier__' + pre_fix + '.jpg'
                    image_store_cashier_filename = fs.save(image_store_cashier_filename, image_store_cashier)
                    image_store_cashier_url = fs.url(image_store_cashier_filename)

                    sale_report.image_outside = image_outside_url if image_outside_url is not None else None
                    sale_report.image_inside = image_inside_url if image_inside_url is not None else None
                    sale_report.image_store_cashier = image_store_cashier_url if image_store_cashier_url is not None else None
                except Exception as e:
                    return JsonResponse({
                        'status': 500,
                        'message': 'Save file error: ' + str(e),
                    }, status=500)

            if not is_draft and shop_status != '2':
                if cessation_of_business_image is None or cessation_of_business_image == '':
                    return JsonResponse({
                        'status': 400,
                        'message': 'cessation_of_business_image is required',
                    }, status=400)
                try:
                    pre_fix = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d__%H_%M_%S__')

                    cessation_of_business_filename = 'cessation_of_business_image__' + pre_fix + '.jpg'
                    cessation_of_business_image_filename = fs.save(cessation_of_business_filename,
                                                                   cessation_of_business_image)
                    cessation_of_business_image_url = fs.url(cessation_of_business_image_filename)

                    sale_report.cessation_of_business_image = cessation_of_business_image if cessation_of_business_image_url is not None else None
                except Exception as e:
                    return JsonResponse({
                        'status': 500,
                        'message': 'Save file error: ' + str(e),
                    }, status=500)

        sale_report.purpose = purpose
        sale_report.longitude = float(longitude)
        sale_report.latitude = float(latitude)
        sale_report.created_by = request.user
        sale_report.updated_by = request.user
        sale_report.is_draft = is_draft

        try:
            sale_report.save()
        except Exception as e:
            return JsonResponse({
                'status': 400,
                'message': 'Save sale_report_form error: ' + str(e),
            }, status=400)

        return JsonResponse({
            'status': 200,
            'data': 'Created',
        }, status=200)

    def retrieve(self, request, pk):
        """
            API get detail Sale_report
        """
        sale_report = get_object_or_404(SaleReport, pk=pk)
        if sale_report.shop_code is not None and sale_report.shop_code != '':
            shop = get_object_or_404(Shop, code=sale_report.shop_code)

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
            'image_outside': sale_report.image_outside.url if sale_report.image_outside else '',
            'image_inside': sale_report.image_inside.url if sale_report.image_inside else '',
            'image_store_cashier': sale_report.image_store_cashier.url if sale_report.image_store_cashier else '',

            # nghỉ kinh doanh
            'cessation_of_business_note': sale_report.cessation_of_business_note,
            'cessation_of_business_image': sale_report.cessation_of_business_image.url if sale_report.cessation_of_business_image else '',

            # chăm sóc
            'customer_care_posm': sale_report.customer_care_posm,
            'customer_care_cashier_reward': sale_report.customer_care_cashier_reward,
            'customer_care_transaction': sale_report.customer_care_transaction,

            # triển khai
            'implement_posm': sale_report.implement_posm,
            'implement_merchant_view': sale_report.implement_merchant_view,
            'implement_career_guideline': sale_report.implement_career_guideline,
            'implement_confirm': sale_report.implement_confirm,
            'implement_new_address': sale_report.implement_new_address
        }

        return JsonResponse({
            'status': 200,
            'data': data
        })
