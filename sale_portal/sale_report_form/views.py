import datetime
from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.utils.html import conditional_escape
from django.core.files.storage import FileSystemStorage

from ..utils.json_response import success_response, error_response
from sale_portal.shop.models import Shop
from .models import SaleReport


def create(request):
    if request.method != 'POST':
        return error_response('002')
    return success_response()

def open_new(request):
    if request.method != 'POST':
        return error_response('002')

    purpose = request.POST.get('purpose', None)
    longitude = request.POST.get('longitude', None)
    latitude = request.POST.get('latitude', None)

    is_draft = request.POST.get('is_draft', None)
    current_draft_id = request.POST.get('current_draft_id', None)

    if longitude is None or longitude == '0' or latitude is None or latitude == '0' or purpose is None:
        return error_response('001')

    if is_draft is None or ( is_draft is not None and current_draft_id is None):
        return error_response('001')

    if str(is_draft).lower() == 'true':
        is_draft = True
        sale_report = get_object_or_404(SaleReport, pk=current_draft_id, is_draft=True)
        if sale_report.created_date.date() != date.today():
            return error_response('003')
    else:
        is_draft = False
        sale_report = SaleReport()

    sale_report = None

    new_merchant_name = request.POST.get('new_merchant_name', None)
    new_merchant_brand = request.POST.get('new_merchant_brand', True)
    new_address = request.POST.get('new_address', None)
    new_note = request.POST.get('new_note', None)
    new_customer_name = request.POST.get('new_customer_name', None)
    new_phone = request.POST.get('new_phone', None)
    new_result = request.POST.get('new_result', None)
    new_using_application = request.POST.get('new_using_application', None)


    sale_report = None
    if current_draft_id is not None:
        sale_report = get_object_or_404(SaleReport, pk=current_draft_id, is_draft=True)



    if purpose == '0':
        sale_report.purpose = purpose
        sale_report.new_merchant_name = conditional_escape(new_merchant_name)
        sale_report.new_merchant_brand = conditional_escape(new_merchant_brand)
        sale_report.new_address = conditional_escape(new_address)
        sale_report.new_customer_name = conditional_escape(new_customer_name)
        sale_report.new_phone = new_phone
        sale_report.new_result = new_result
        sale_report.new_note = new_note
