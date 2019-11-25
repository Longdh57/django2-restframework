import datetime
from datetime import date
import time
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.utils.html import conditional_escape
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework.decorators import api_view

from ..utils.field_formatter import format_string
import sale_portal.utils.field_validator as fv
from sale_portal.shop.models import Shop
from sale_portal.user.models import User
from .models import SaleReport



@api_view(['POST'])
@login_required
@permission_required('sale_report_form.sale_report_create', raise_exception=True)
def store(request):
    # required data fields from request
    purpose = request.POST.get('purpose', None)
    longitude = request.POST.get('longitude', None)
    latitude = request.POST.get('latitude', None)
    is_draft = request.POST.get('is_draft', None)
    current_draft_id = request.POST.get('current_draft_id', None)

    if purpose is None\
            or longitude is None or longitude == '0'\
            or latitude is None or latitude == '0'\
            or is_draft is None:
        return JsonResponse({
            'status': 'FAILURE',
            'error': 'Some data fields such as purpose, longitude, latitude, is_draft are required',
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
            'status': 'FAILURE',
            'error': 'Only allow access to drafts created on today',
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
    image_store_cashier = request.FILES['image_store_cashier'] if 'image_store_cashier' in request.FILES else None

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
    image_outside_url = None
    image_inside_url = None
    image_store_cashier_url = None
    cessation_of_business_image_url = None

    # ingest data to sale_report object
    purpose = format_string(purpose, True)
    if purpose not in ['0','1','2']:
        return JsonResponse({
            'status': 'FAILURE',
            'error': 'Purpose is incorrect',
        }, status=400)
    if purpose == '0':
        sale_report.purpose = purpose
        sale_report.new_merchant_name = format_string(new_merchant_name, True)
        sale_report.new_merchant_brand = format_string(new_merchant_brand, True)
        sale_report.new_address = format_string(new_address, True)
        sale_report.new_customer_name = format_string(new_customer_name, True)
        sale_report.new_phone = format_string(new_phone, True)
        sale_report.new_result = format_string(new_result, True)
        sale_report.new_note = format_string(new_note, True)
        sale_report.new_using_application = format_string(new_using_application, True)
        #validate
        try:
            fv.validate_merchant_name(new_merchant_name, False, False, True)
            fv.validate_merchant_brand(new_merchant_brand, True, True, True)
            fv.validate_address(new_address, True, True, True)
            fv.validate_customer_name(new_customer_name, True, True, True)
            fv.validate_phone(new_phone, True, True, True)
            fv.validate_in_string_list(['0', '1', '2', '3'],\
                                       'new_result', new_result, False, False, True)
            fv.validate_note(new_note, True, True, True)
            fv.validate_in_string_list(['iPos', 'Sapo', 'KiotViet', 'POS365', 'Cukcuk', 'Ocha', 'PM khác', 'Chưa sử dụng'], \
                                       'new_using_application', new_using_application, True, True, True)
        except Exception as e:
            return JsonResponse({
                'status': 'FAILURE',
                'error': 'Validate error: '+str(e),
            }, status=400)

    elif purpose == '1':
        shop = get_object_or_404(Shop, pk=shop_id)

        sale_report.shop_code = shop.code
        sale_report.implement_posm = format_string(implement_posm)
        sale_report.implement_merchant_view = format_string(implement_merchant_view, True)
        sale_report.implement_career_guideline = format_string(implement_career_guideline, True)
        sale_report.implement_confirm = format_string(implement_confirm, True)
        implement_new_address = format_string(implement_new_address, True)
        try:
            fv.validate_in_string_list(['0', '1', '2'], \
                                       'verify_shop', implement_confirm, False, False, True)
            if implement_confirm == '1':
                fv.validate_address(implement_new_address, False, False, True)
                sale_report.implement_new_address = implement_new_address
        except Exception as e:
            return JsonResponse({
                'status': 'FAILURE',
                'error': 'Validate error: ' + str(e),
            }, status=400)

        # save image
        if not is_draft:
            if image_outside is None or image_outside == ''\
                    or image_inside is None or image_inside == ''\
                    or image_store_cashier is None and image_store_cashier == '':
                return JsonResponse({
                    'status': 'FAILURE',
                    'error': 'image_outside, image_inside, image_store_cashier are required',
                }, status=400)
            try:
                pre_fix = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d__%H_%M_%S__')

                image_outside_filename, image_outside_file_extension = os.path.splitext(image_outside.name)
                if image_outside_file_extension not in ['.png', '.jpg']:
                    return JsonResponse({
                        'status': 'FAILURE',
                        'error': 'file_extension is invalid',
                    }, status=400)
                image_outside_filename = image_outside_filename[:100] if len(
                    image_outside_filename) > 100 else image_outside_filename
                image_outside_filename = 'image_outside__' + pre_fix + image_outside_filename + '.jpg'
                image_outside_filename = fs.save(image_outside_filename, image_outside)
                image_outside_url = fs.url(image_outside_filename)

                image_inside_filename, image_inside_file_extension = os.path.splitext(image_inside.name)
                if image_inside_file_extension not in ['.png', '.jpg']:
                    return JsonResponse({
                        'status': 'FAILURE',
                        'error': 'file_extension is invalid',
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
                        'status': 'FAILURE',
                        'error': 'file_extension is invalid',
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
                    'status': 'FAILURE',
                    'error': 'Save file error: ' + str(e),
                }, status=500)
    else:
        shop = get_object_or_404(Shop, pk=shop_id)
        pre_fix = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d__%H_%M_%S__')

        if image_outside is not None and image_outside != '' and not is_draft:
            image_outside_filename, image_outside_file_extension = os.path.splitext(image_outside.name)
            if image_outside_file_extension not in ['.png', '.jpg']:
                return JsonResponse({
                    'status': 'FAILURE',
                    'error': 'file_extension is invalid',
                }, status=400)
            image_outside_filename = image_outside_filename[:100] if len(image_outside_filename) > 100 else image_outside_filename
            image_outside_filename = 'image_outside__' + pre_fix + image_outside_filename + '.jpg'
            image_outside_filename = fs.save(image_outside_filename, image_outside)
            image_outside_url = fs.url(image_outside_filename)

        if image_inside is not None and image_inside != '' and not is_draft:
            image_inside_filename, image_inside_file_extension = os.path.splitext(image_inside.name)
            if image_inside_file_extension not in ['.png', '.jpg']:
                return JsonResponse({
                    'status': 'FAILURE',
                    'error': 'file_extension is invalid',
                }, status=400)
            image_inside_filename = image_inside_filename[:100] if len(
                image_inside_filename) > 100 else image_inside_filename
            image_inside_filename = 'image_inside__' + pre_fix + image_inside_filename + '.jpg'
            image_inside_filename = fs.save(image_inside_filename, image_inside)
            image_inside_url = fs.url(image_inside_filename)

        if image_store_cashier is not None and image_store_cashier != '' and not is_draft:
            image_store_cashier_filename, image_store_cashier_file_extension = os.path.splitext(
                image_store_cashier.name)
            if image_store_cashier_file_extension not in ['.png', '.jpg']:
                return JsonResponse({
                    'status': 'FAILURE',
                    'error': 'file_extension is invalid',
                }, status=400)
            image_store_cashier_filename = image_store_cashier_filename[:100] if len(
                image_store_cashier_filename) > 100 else image_store_cashier_filename
            image_store_cashier_filename = 'image_store_cashier__' + pre_fix + image_store_cashier_filename + '.jpg'
            image_store_cashier_filename = fs.save(image_store_cashier_filename, image_store_cashier)
            image_store_cashier_url = fs.url(image_store_cashier_filename)

        if cessation_of_business_image is not None and cessation_of_business_image != '' and not is_draft:
            cessation_of_business_filename, cessation_of_business_file_extension = os.path.splitext(cessation_of_business_image.name)
            if cessation_of_business_file_extension not in ['.png', '.jpg']:
                return JsonResponse({
                    'status': 'FAILURE',
                    'error': 'file_extension is invalid',
                }, status=400)
            cessation_of_business_filename = cessation_of_business_filename[:100] if len(cessation_of_business_filename) > 100 else cessation_of_business_filename
            cessation_of_business_filename = 'cessation_of_business_image__' + pre_fix + cessation_of_business_filename + '.jpg'
            cessation_of_business_image_filename = fs.save(cessation_of_business_filename, cessation_of_business_image)
            cessation_of_business_image_url = fs.url(cessation_of_business_image_filename)

        sale_report.shop_code = shop.code
        sale_report.shop_status = shop_status
        sale_report.image_outside = image_outside_url
        sale_report.image_inside = image_inside_url
        sale_report.image_store_cashier = image_store_cashier_url
        sale_report.cessation_of_business_note = conditional_escape(cessation_of_business_note)
        sale_report.cessation_of_business_image = cessation_of_business_image if cessation_of_business_image_url is not None else None
        sale_report.customer_care_posm = customer_care_posm
        sale_report.customer_care_cashier_reward = customer_care_cashier_reward if customer_care_cashier_reward is not None and customer_care_cashier_reward != 'undefined' else None
        sale_report.customer_care_transaction = customer_care_transaction if customer_care_transaction is not None and customer_care_transaction != '' else None

    sale_report.purpose = purpose if purpose is not None and purpose != '' else 0
    sale_report.longitude = float(longitude)
    sale_report.latitude = float(latitude)
    sale_report.created_by = request.user
    sale_report.updated_by = request.user
    sale_report.is_draft = is_draft

    sale_report.save()
    return JsonResponse({
        'status': 'SUCCESS',
        'data': 'Created',
    }, status=200)
