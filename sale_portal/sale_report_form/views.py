import datetime
from datetime import date

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.html import conditional_escape
from django.core.files.storage import FileSystemStorage

from ..utils.json_response import success_response, error_response
from sale_portal.shop.models import Shop
from .models import SaleReport

def create(request):
    if request.method != 'POST':
        return error_response('002')

    purpose = request.POST.get('purpose', None)
    longitude = request.POST.get('longitude', None)
    latitude = request.POST.get('latitude', None)

    new_merchant_name = request.POST.get('new_merchant_name', None)
    new_merchant_brand = request.POST.get('new_merchant_brand', True)
    new_address = request.POST.get('new_address', None)
    new_note = request.POST.get('new_note', None)
    new_customer_name = request.POST.get('new_customer_name', None)
    new_phone = request.POST.get('new_phone', None)
    new_result = request.POST.get('new_result', None)

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

    is_draft = request.POST.get('is_draft', None)
    current_draft_id = request.POST.get('current_draft_id', None)

    if is_draft == 'true':
        is_draft = True
    else:
        is_draft = False

    sale_report = None
    if current_draft_id is not None:
        sale_report = get_object_or_404(SaleReport, pk=current_draft_id, is_draft=True)

    if longitude is None or longitude == '0' or latitude is None or latitude == '0' or is_draft is None:
        return error_response('001')

    fs = FileSystemStorage(
        location=settings.FS_IMAGE_UPLOADS + datetime.date.today().isoformat(),
        base_url=settings.FS_IMAGE_URL + datetime.date.today().isoformat()
    )

    image_outside_url = None
    image_inside_url = None
    image_store_cashier_url = None
    cessation_of_business_image_url = None
    if sale_report is None:
        sale_report = SaleReport()
    elif sale_report.created_date.date() != date.today():
        return False

    if purpose == '0':
        sale_report.purpose = purpose
        sale_report.new_merchant_name = conditional_escape(new_merchant_name)
        sale_report.new_merchant_brand = conditional_escape(new_merchant_brand)
        sale_report.new_address = conditional_escape(new_address)
        sale_report.new_customer_name = conditional_escape(new_customer_name)
        sale_report.new_phone = new_phone
        sale_report.new_result = new_result
        sale_report.new_note = new_note

    elif purpose == '1':
        shop = Shop.objects.get(pk=shop_id)

        if image_outside is not None and image_outside != '' and not is_draft:
            image_outside_filename = fs.save(image_outside.name+'.jpg', image_outside)
            image_outside_url = fs.url(image_outside_filename)

        if image_inside is not None and image_inside != '' and not is_draft:
            image_inside_filename = fs.save(image_inside.name+'.jpg', image_inside)
            image_inside_url = fs.url(image_inside_filename)

        if image_store_cashier is not None and image_store_cashier != '' and not is_draft:
            image_store_cashier_filename = fs.save(image_store_cashier.name+'.jpg', image_store_cashier)
            image_store_cashier_url = fs.url(image_store_cashier_filename)

        sale_report.shop_code = shop.code
        sale_report.image_outside = image_outside_url if image_outside_url is not None else None
        sale_report.image_inside = image_inside_url if image_inside_url is not None else None
        sale_report.image_store_cashier = image_store_cashier_url if image_store_cashier_url is not None else None
        sale_report.implement_posm = implement_posm
        sale_report.implement_merchant_view = implement_merchant_view
        sale_report.implement_career_guideline = implement_career_guideline
        sale_report.implement_confirm = implement_confirm
        sale_report.implement_new_address = implement_new_address
    else:
        shop = Shop.objects.get(pk=shop_id)

        if image_outside is not None and image_outside != '' and not is_draft:
            image_outside_filename = fs.save(image_outside.name+'.jpg', image_outside)
            image_outside_url = fs.url(image_outside_filename)

        if image_inside is not None and image_inside != '' and not is_draft:
            image_inside_filename = fs.save(image_inside.name+'.jpg', image_inside)
            image_inside_url = fs.url(image_inside_filename)

        if image_store_cashier is not None and image_store_cashier != '' and not is_draft:
            image_store_cashier_filename = fs.save(image_store_cashier.name+'.jpg', image_store_cashier)
            image_store_cashier_url = fs.url(image_store_cashier_filename)

        if cessation_of_business_image is not None and cessation_of_business_image != '' and not is_draft:
            cessation_of_business_image_filename = fs.save(cessation_of_business_image.name+'.jpg',
                                                           cessation_of_business_image)
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

    return success_response()