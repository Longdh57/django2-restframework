import datetime
from datetime import date
from datetime import datetime as dt_datetime
import time
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view

from sale_portal.staff.models import Staff
from ..utils.field_formatter import format_string
import sale_portal.utils.field_validator as fv
from sale_portal.shop.models import Shop
from .models import SaleReport
from .serializers import SaleReportSerializer
from sale_portal.user.models import User
from sale_portal.team.models import Team


class SaleReportViewSet(viewsets.ModelViewSet):
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

            Các trường bắt buộc cho tất cả loại báo cáo   \n
                purpose:2   \n
                longitude:100.15526   \n
                latitude:101.5656   \n
                is_draft:true   \n

            Nếu đang tạo báo cáo trên bản nháp đã có thì cần truyền id bản nháp lên   \n
                current_draft_id:1   \n

            Các trường cho báo cáo mở mới   \n
            Trường bắt buộc:   \n
                new_merchant_name:test new_merchant_name   \n
                new_result:0   \n
            Các trường khác:   \n
                new_merchant_brand:merchant brand   \n
                new_address:test new_address   \n
                new_customer_name:test dnew customer name   \n
                new_phone:+8412345678   \n
                new_note:note   \n
                new_using_application:iPos   \n

            Các trường cho báo cáo triển khai   \n
            Trường bắt buộc   \n
                shop_id:1   \n
                verify_shop:1   \n
                implement_merchant_view:Web, App   \n
                image_outside:image   \n
                image_inside:image   \n
                image_store_cashier:image   \n
            Nếu verify_shop:1 bắt buộc   \n
                new_address_input:Hà Nội   \n
            Các trường khác   \n
                implement_career_guideline:Cửa hàng trưởng, Thu ngân   \n
                implement_posm:[{"standeeQr":"2","stickerDoor":"4","stickerTable":"4","guide":"4","wobbler":"4","poster":"3","standeeCtkm":"4","tentcard":"4"}]   \n

            Các trường cho tạo báo cáo triển khai   \n
            Bắt buộc   \n
                 shop_id:1   \n
                 shop_status:2   \n
            Nếu shop_status:2   \n
            Cần các trường   \n
            Bắt buộc   \n
                image_outside:image   \n
                image_inside:image   \n
                image_store_cashier:image   \n
                customer_care_transaction:142   \n
                customer_care_cashier_reward:1   \n
            Các trường khác   \n
                implement_posm:[{"standeeQr":"2","stickerDoor":"4","stickerTable":"4","guide":"4","wobbler":"4","poster":"3","standeeCtkm":"4","tentcard":"4"}]   \n
            Các shop_status còn lại thì   \n
            Cần các trường   \n
            Bắt buộc   \n
                cessation_of_business_note:abc   \n
                cessation_of_business_image:image   \n
            Chú ý: nếu là bản nháp ko cần upload ảnh

        """
        # required data fields from request
        purpose = request.POST.get('purpose', None)
        longitude = request.POST.get('longitude', None)
        latitude = request.POST.get('latitude', None)
        is_draft = request.POST.get('is_draft', None)
        current_draft_id = request.POST.get('current_draft_id', None)

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

        # open_new_shop purpose data from request
        new_merchant_name = request.POST.get('new_merchant_name', None)
        new_merchant_brand = request.POST.get('new_merchant_brand', True)
        new_address = request.POST.get('new_address', None)
        new_customer_name = request.POST.get('new_customer_name', None)
        new_phone = request.POST.get('new_phone', None)
        new_result = request.POST.get('new_result', None)
        new_note = request.POST.get('new_note', None)
        new_using_application = request.POST.get('new_using_application', None)

        # other purpose data from request
        shop_id = request.POST.get('shop_id', None)
        shop_status = request.POST.get('shop_status', None)
        image_outside = request.FILES['image_outside'] if 'image_outside' in request.FILES else None
        image_inside = request.FILES['image_inside'] if 'image_inside' in request.FILES else None
        image_store_cashier = request.FILES[
            'image_store_cashier'] if 'image_store_cashier' in request.FILES else None

        cessation_of_business_note = request.POST.get('cessation_of_business_note', None)
        cessation_of_business_image = request.FILES[
            'cessation_of_business_image'] if 'cessation_of_business_image' in request.FILES else None

        customer_care_posm = request.POST.get('customer_care_posm', None)
        customer_care_cashier_reward = request.POST.get('customer_care_cashier_reward', None)
        customer_care_transaction = request.POST.get('customer_care_transaction', None)

        implement_posm = request.POST.get('implement_posm', None)
        implement_merchant_view = request.POST.get('implement_merchant_view')
        implement_career_guideline = request.POST.get('implement_career_guideline')
        implement_confirm = request.POST.get('verify_shop')
        implement_new_address = request.POST.get('new_address_input')

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
            try:
                fv.validate_merchant_name(format_string(new_merchant_name), False, False, True)
                fv.validate_merchant_brand(format_string(new_merchant_brand), True, True, True)
                fv.validate_address(format_string(new_address), True, True, True)
                fv.validate_customer_name(format_string(new_customer_name), True, True, True)
                fv.validate_phone(format_string(new_phone), True, True, True)
                fv.validate_in_string_list(['0', '1', '2', '3'], \
                                           'new_result', format_string(new_result), False, False, True)
                fv.validate_note(format_string(new_note), True, True, True)
                fv.validate_in_string_list(
                    ['iPos', 'Sapo', 'KiotViet', 'POS365', 'Cukcuk', 'Ocha', 'PM khác', 'Chưa sử dụng'], \
                    'new_using_application', format_string(new_using_application), True, True, True)

                sale_report.new_merchant_name = format_string(new_merchant_name, True)
                sale_report.new_merchant_brand = format_string(new_merchant_brand, True)
                sale_report.new_address = format_string(new_address, True)
                sale_report.new_customer_name = format_string(new_customer_name, True)
                sale_report.new_phone = format_string(new_phone, True)
                sale_report.new_result = format_string(new_result, True)
                sale_report.new_note = format_string(new_note, True)
                sale_report.new_using_application = format_string(new_using_application, True)
            except Exception as e:
                return JsonResponse({
                    'status': 400,
                    'message': 'Validate error: ' + str(e),
                }, status=400)

        elif purpose == '1':
            shop = get_object_or_404(Shop, pk=shop_id)
            sale_report.shop_code = shop.code
            try:
                fv.validate_in_string_list(['0', '1', '2'], \
                                           'verify_shop', implement_confirm, False, False, True)
                if implement_merchant_view is None:
                    raise Exception('implement_merchant_view is required')
                sale_report.implement_posm = format_string(implement_posm, True)
                sale_report.implement_merchant_view = format_string(implement_merchant_view, True)
                sale_report.implement_career_guideline = format_string(implement_career_guideline, True)
                sale_report.implement_confirm = format_string(implement_confirm, True)
                if implement_confirm == '1':
                    fv.validate_address(format_string(implement_new_address), False, False, True)
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

                    image_outside_filename, image_outside_file_extension = os.path.splitext(image_outside.name)
                    if image_outside_file_extension not in ['.png', '.jpg']:
                        return JsonResponse({
                            'status': 400,
                            'message': 'file_extension is invalid',
                        }, status=400)
                    image_outside_filename = image_outside_filename[:100] if len(
                        image_outside_filename) > 100 else image_outside_filename
                    image_outside_filename = 'image_outside__' + pre_fix + image_outside_filename + '.jpg'
                    image_outside_filename = fs.save(image_outside_filename, image_outside)
                    image_outside_url = fs.url(image_outside_filename)

                    image_inside_filename, image_inside_file_extension = os.path.splitext(image_inside.name)
                    if image_inside_file_extension not in ['.png', '.jpg']:
                        return JsonResponse({
                            'status': 400,
                            'message': 'file_extension is invalid',
                        }, status=400)
                    image_inside_filename = image_inside_filename[:100] if len(
                        image_inside_filename) > 100 else image_inside_filename
                    image_inside_filename = 'image_inside__' + pre_fix + image_inside_filename + '.jpg'
                    image_inside_filename = fs.save(image_inside_filename, image_inside)
                    image_inside_url = fs.url(image_inside_filename)

                    image_store_cashier_filename, image_store_cashier_file_extension = os.path.splitext(
                        image_store_cashier.name)
                    if image_store_cashier_file_extension not in ['.png', '.jpg']:
                        return JsonResponse({
                            'status': 400,
                            'message': 'file_extension is invalid',
                        }, status=400)
                    image_store_cashier_filename = image_store_cashier_filename[:100] if len(
                        image_store_cashier_filename) > 100 else image_store_cashier_filename
                    image_store_cashier_filename = 'image_store_cashier__' + pre_fix + image_store_cashier_filename + '.jpg'
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
                fv.validate_in_string_list(['0', '1', '2', '3', '4'], 'shop_status', format_string(shop_status),
                                           False,
                                           False, True)
                sale_report.shop_status = format_string(shop_status, True)
                if sale_report.shop_status == '2':
                    fv.validate_in_string_list(['0', '1'], 'customer_care_cashier_reward',
                                               format_string(customer_care_cashier_reward), False, False, True)
                    fv.validate_transaction(format_string(customer_care_transaction), False, False, True)
                    sale_report.customer_care_cashier_reward = format_string(customer_care_cashier_reward, True)
                    sale_report.customer_care_transaction = format_string(customer_care_transaction, True)
                else:
                    fv.validate_note(format_string(cessation_of_business_note), False, False, True)
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

                    image_outside_filename, image_outside_file_extension = os.path.splitext(image_outside.name)
                    if image_outside_file_extension not in ['.png', '.jpg']:
                        return JsonResponse({
                            'status': 400,
                            'message': 'file_extension is invalid',
                        }, status=400)
                    image_outside_filename = image_outside_filename[:100] if len(
                        image_outside_filename) > 100 else image_outside_filename
                    image_outside_filename = 'image_outside__' + pre_fix + image_outside_filename + '.jpg'
                    image_outside_filename = fs.save(image_outside_filename, image_outside)
                    image_outside_url = fs.url(image_outside_filename)

                    image_inside_filename, image_inside_file_extension = os.path.splitext(image_inside.name)
                    if image_inside_file_extension not in ['.png', '.jpg']:
                        return JsonResponse({
                            'status': 400,
                            'message': 'file_extension is invalid',
                        }, status=400)
                    image_inside_filename = image_inside_filename[:100] if len(
                        image_inside_filename) > 100 else image_inside_filename
                    image_inside_filename = 'image_inside__' + pre_fix + image_inside_filename + '.jpg'
                    image_inside_filename = fs.save(image_inside_filename, image_inside)
                    image_inside_url = fs.url(image_inside_filename)

                    image_store_cashier_filename, image_store_cashier_file_extension = os.path.splitext(
                        image_store_cashier.name)
                    if image_store_cashier_file_extension not in ['.png', '.jpg']:
                        return JsonResponse({
                            'status': 400,
                            'message': 'file_extension is invalid',
                        }, status=400)
                    image_store_cashier_filename = image_store_cashier_filename[:100] if len(
                        image_store_cashier_filename) > 100 else image_store_cashier_filename
                    image_store_cashier_filename = 'image_store_cashier__' + pre_fix + image_store_cashier_filename + '.jpg'
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
                    cessation_of_business_filename, cessation_of_business_file_extension = os.path.splitext(
                        cessation_of_business_image.name)
                    if cessation_of_business_file_extension not in ['.png', '.jpg']:
                        return JsonResponse({
                            'status': 400,
                            'message': 'file_extension is invalid',
                        }, status=400)
                    cessation_of_business_filename = cessation_of_business_filename[:100] if len(
                        cessation_of_business_filename) > 100 else cessation_of_business_filename
                    cessation_of_business_filename = 'cessation_of_business_image__' + pre_fix + cessation_of_business_filename + '.jpg'
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
        sale_report.save()
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