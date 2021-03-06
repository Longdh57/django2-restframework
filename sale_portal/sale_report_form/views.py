import ast
import base64
import datetime
import json
import os
import time as time_t
from datetime import date, time, timedelta
from datetime import datetime as dt_datetime
from time import time as time_f

import xlsxwriter
from django.contrib.auth.decorators import login_required, permission_required
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import formats
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view

from sale_portal import settings
from sale_portal.common.standard_response import successful_response
from sale_portal.sale_report_form import SaleReportFormPurposeTypes
from sale_portal.sale_report_form.models import SaleReport
from sale_portal.sale_report_form.serializers import SaleReportSerializer
from sale_portal.sale_report_form.serializers import SaleReportStatisticSerializer
from sale_portal.shop.models import Shop
from sale_portal.staff.models import Staff
from sale_portal.user.models import User
from sale_portal.utils import field_validator
from sale_portal.utils.excel_util import check_or_create_excel_folder
from sale_portal.utils.field_formatter import format_string
from sale_portal.utils.permission import get_user_permission_classes
from sale_portal.utils.queryset import get_users_viewable_queryset


class SaleReportViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = SaleReportSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('sale_report_form.report_list_data', self.request)
        if self.action == 'retrieve':
            permission_classes = get_user_permission_classes('sale_report_form.report_detail_data', self.request)
        if self.action == 'create':
            permission_classes = get_user_permission_classes('sale_report_form.create_sale_report', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
            API get list SaleReport   \n
            filter theo c??c param purpose,shop_id ,user,team_id,from_date,to_date \n
            C?? th??? b??? tr???ng
        """
        return get_list_queryset(self.request)

    def create(self, request):
        """
            API create SaleReport   \n

            HelpText - (* l?? b???t bu???c) code - dataType - List gi?? tr??? (l?? {} n???u kh??ng c??) - V?? d???   \n

            C??c tr?????ng b???t bu???c cho t???t c??? lo???i b??o c??o   \n
                M???c ????ch - *purpose - string(10) - ['0': 'M??? m???i', '1': 'Tri???n khai', '2': 'Ch??m s??c'] - purpose: '0'  \n
                LON - *longitude - float - {} - longitude: 105.8226176   \n
                LAT - *latitude - float - {} - latitude :101.5656   \n
                B???n nh??p hay ch??nh th???c - *is_draft - boolean - {} - is_draft: true   \n

            N???u ??ang t???o b??o c??o tr??n b???n nh??p ???? c?? th?? c???n truy???n id b???n nh??p l??n   \n
                ID b???n nh??p - current_draft_id - int - {} - current_draft_id: 10   \n

            C??c tr?????ng cho b??o c??o m??? m???i   \n
                T??n merchant - *new_merchant_name - string(255) - {} - new_merchant_name: 'HotPot Story'   \n
                Th????ng hi???u - new_merchant_brand - string(255) - {} - new_merchant_brand: 'RedSun'    \n
                ?????a ch??? - new_address - text - {} - new_address: '36 Ho??ng C???u'   \n
                T??n ng?????i li??n h??? - new_customer_name - string(255) - {} - new_customer_name: 'Nguy???n Th??? Th??y'   \n
                S??T li??n h??? - new_phone - string(100) - {} - new_phone: '012345678'   \n
                K???t qu??? m??? m???i - *new_result - int - [0: 'Dong y, da ky duoc HD', 1: 'Dong y, chua ky duoc HD', 2: 'Can xem xet them', 3: 'Tu choi hop tac'] - new_result: 0   \n
                MC ??ang s??? d???ng PM b??n h??ng - new_using_application - string(100) - ['iPos', 'Sapo', 'KiotViet', 'POS365', 'Cukcuk', 'Ocha', 'PM kh??c', 'Ch??a s??? d???ng'] - new_using_application: 'iPos'   \n
                Ghi ch?? - new_note - text - {} - new_note: '????y l?? ghi ch?? test xxxx'   \n

            C??c tr?????ng d??ng chung cho b??o c??o tri???n khai & ch??m s??c   \n
                C???a h??ng - *shop_id - int - {} - shop_id: 47215  \n
                HA nghi???m thu (Ngo??i CH) - *image_outside - binary - {} - image_outside: (binary)   \n
                HA nghi???m thu (Trong CH) - *image_inside - binary - {} - image_inside: (binary)   \n
                HA nghi???m thu (Qu???y thu ng??n) - *image_store_cashier - binary - {} - image_store_cashier: (binary)   \n
                B??? posm tri???n khai bao g???m - standeeQr - int - {} - standeeQr: 2   \n
                B??? posm tri???n khai bao g???m - stickerTable - int - {} - stickerTable: 2   \n
                B??? posm tri???n khai bao g???m - wobbler - int - {} - wobbler: 2   \n
                B??? posm tri???n khai bao g???m - standeeCtkm - int - {} - standeeCtkm: 2   \n
                B??? posm tri???n khai bao g???m - stickerDoor - int - {} - stickerDoor: 2   \n
                B??? posm tri???n khai bao g???m - guide - int - {} - guide: 2   \n
                B??? posm tri???n khai bao g???m - poster - int - {} - poster: 2   \n
                B??? posm tri???n khai bao g???m - tentcard - int - {} - tentcard: 2   \n

            C??c tr?????ng cho t???o b??o c??o tri???n khai   \n
                X??c th???c shop - *implement_confirm - int - [0, 1, 2] - implement_confirm: 1   \n
                Merchant view cho Terminal g???m - *implement_merchant_view - array() - [1: 'web', 2: 'app', 3: 'other'] - implement_merchant_view: [2, 3]   \n
                ???? h?????ng d???n nghi???p v??? cho - *implement_career_guideline - array() - [0: 'Thu ng??n', 1: 'C???a h??ng tr?????ng'] - implement_career_guideline: [0, 1]   \n
            N???u Tri???n khai - implement_confirm = 1 th?? nh???p th??m tr?????ng   \n
                ?????a ch??? m???i - *implement_new_address - text - {} - implement_new_address: '34 Ph??ng H??ng'   \n

            C??c tr?????ng cho t???o b??o c??o ch??m s??c   \n
                T??nh tr???ng c???a h??ng - *shop_status - int - [0: 'Da nghi kinh doanh/ khong co cua hang thuc te', 1: 'Muon thanh ly QR', 2: 'Dang hoat dong', 3: 'Kh??ng h???p t??c', 4: 'Da chuyen dia diem'] - shop_status: 2  \n
            N???u shop_status <> 2 kh??ng upload 3 ???nh nh??ng th??m 2 tr?????ng sau  \n
                M?? t??? - *cessation_of_business_note - text - {} - cessation_of_business_note: 'Kh??ng t??m ???????c c???a h??ng ????? ch??m s??c'   \n
                ???nh nghi???m thu - *cessation_of_business_image - binary - {} - cessation_of_business_image: (binary)   \n
            N???u shop_status = 2 c???n upload 3 ???nh & th??m c??c tr?????ng d?????i  \n
                K?? H?? th?????ng thu ng??n kh??ng - *customer_care_cashier_reward - int - [0: 'Kh??ng', 1: 'C??'] - customer_care_cashier_reward: 0   \n
                S??? giao d???ch ph??t sinh trong th???i gian ch??m s??c - *transaction - int - {} - transaction: 4   \n

            Ch?? ??: n???u l?? b???n nh??p ko c???n upload ???nh - Kh??ng push ???nh l??n server   \n

        """

        # Data nh???n d?????i d???ng form data, sau ???? convert ra json r???i x??? l??
        data = request.POST.get('data', None)
        datajson = json.loads(data)

        purpose = datajson.get('purpose')
        longitude = datajson.get('longitude')
        latitude = datajson.get('latitude')
        is_draft = datajson.get('is_draft')
        current_draft_id = datajson.get('current_draft_id')
        # validate purpose, longitude, latitude, is_draft
        if purpose is None \
                or longitude is None or str(longitude) == '0' \
                or latitude is None or str(latitude) == '0' \
                or is_draft is None:
            return self.response(
                status=400, message='Validate error: purpose, longitude, latitude, is_draft are required')

        purpose = format_string(purpose, True)
        if str(purpose) not in ['0', '1', '2']:
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

        # Tao folder save image
        location = settings.FS_IMAGE_UPLOADS + datetime.date.today().isoformat()
        base_url = settings.FS_IMAGE_URL + datetime.date.today().isoformat()
        if not os.path.exists(location):
            os.makedirs(location)

        # Xu ly request M??? M???i
        if str(purpose) == '0':
            new_merchant_name = datajson.get('new_merchant_name')
            new_merchant_brand = datajson.get('new_merchant_brand')
            new_address = datajson.get('new_address')
            new_customer_name = datajson.get('new_customer_name')
            new_phone = datajson.get('new_phone')
            new_result = datajson.get('new_result')
            new_note = datajson.get('new_note')
            new_using_application = datajson.get('new_using_application')
            new_store_image = datajson.get('new_store_image')

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
                    'PM kh??c',
                    'Ch??a s??? d???ng'
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

            if not is_draft:
                if new_store_image is None or new_store_image == '':
                    return self.response(
                        status=400, message='new_store_image is required')
                new_store_image_filename = str(request.user.username) + '-new_store_image' + str(
                    time_f()) + '.png'
                with open(location + '/' + new_store_image_filename, "wb") as f:
                    f.write(base64.b64decode(new_store_image))
                    f.close()
                    sale_report.new_store_image = base_url + '/' + new_store_image_filename

        # Xu ly request Tri???n khai
        elif str(purpose) == '1':
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
                if str(implement_confirm) == '1':
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
                    image_outside_filename = str(request.user.username) + '-image_outside' + str(time_f()) + '.png'
                    with open(location + '/' + image_outside_filename, "wb") as f:
                        f.write(base64.b64decode(image_outside_v2))
                        f.close()
                        sale_report.image_outside_v2 = base_url + '/' + image_outside_filename

                    image_inside_filename = str(request.user.username) + '-image_inside' + str(time_f()) + '.png'
                    with open(location + '/' + image_inside_filename, "wb") as f:
                        f.write(base64.b64decode(image_inside_v2))
                        f.close()
                        sale_report.image_inside_v2 = base_url + '/' + image_inside_filename

                    image_store_cashier_filename = str(request.user.username) + '-image_store_cashier' + str(
                        time_f()) + '.png'
                    with open(location + '/' + image_store_cashier_filename, "wb") as f:
                        f.write(base64.b64decode(image_store_cashier_v2))
                        f.close()
                        sale_report.image_store_cashier_v2 = base_url + '/' + image_store_cashier_filename

        # Xu ly request Ch??m s??c
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

            customer_care_cashier_reward = str(datajson.get('customer_care_cashier_reward'))
            customer_care_transaction = str(datajson.get('transaction'))

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

                image_outside_filename = str(request.user.username) + '-image_outside' + str(time_f()) + '.png'
                with open(location + '/' + image_outside_filename, "wb") as f:
                    f.write(base64.b64decode(image_outside))
                    f.close()
                    sale_report.image_outside_v2 = base_url + '/' + image_outside_filename

                image_inside_filename = str(request.user.username) + '-image_inside' + str(time_f()) + '.png'
                with open(location + '/' + image_inside_filename, "wb") as f:
                    f.write(base64.b64decode(image_inside))
                    f.close()
                    sale_report.image_inside_v2 = base_url + '/' + image_inside_filename

                image_store_cashier_filename = str(request.user.username) + '-image_store_cashier' + str(
                    time_f()) + '.png'
                with open(location + '/' + image_store_cashier_filename, "wb") as f:
                    f.write(base64.b64decode(image_store_cashier))
                    f.close()
                    sale_report.image_store_cashier_v2 = base_url + '/' + image_store_cashier_filename

            if not is_draft and shop_status != 2:
                if cessation_of_business_image_v2 is None or cessation_of_business_image_v2 == '':
                    return self.response(
                        status=400, message='cessation_of_business_image is required')

                cessation_of_business_image_filename = str(request.user.username) + '-cessation_of_business' + str(
                    time_f()) + '.png'
                with open(location + '/' + cessation_of_business_image_filename, "wb") as f:
                    f.write(base64.b64decode(cessation_of_business_image_v2))
                    f.close()
                    sale_report.cessation_of_business_image_v2 = base_url + '/' + cessation_of_business_image_filename

        sale_report.purpose = purpose
        sale_report.longitude = float(longitude)
        sale_report.latitude = float(latitude)
        sale_report.created_by = request.user
        sale_report.updated_by = request.user
        sale_report.is_draft = is_draft
        if not is_draft and str(purpose) == '2':
            shop.take_care_status = 2
            shop.save()

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
            new_store_image = sale_report.new_store_image or None
            image_outside = sale_report.image_outside.url if sale_report.image_outside else ''
            image_inside = sale_report.image_inside.url if sale_report.image_inside else ''
            image_store_cashier = sale_report.image_store_cashier.url if sale_report.image_store_cashier else ''
            cessation_of_business_image = sale_report.cessation_of_business_image.url if sale_report.cessation_of_business_image else ''
            posm = None
            implement_merchant_view = sale_report.implement_merchant_view
            implement_career_guideline = sale_report.implement_career_guideline
            if implement_merchant_view is not None:
                implement_merchant_view = '[' + implement_merchant_view + ']'
                implement_merchant_view = implement_merchant_view.replace('0', "'Web'") \
                    .replace('1', "'App'").replace('2', "'Other'")
            if implement_career_guideline is not None:
                implement_career_guideline = '[' + implement_career_guideline + ']'
                implement_career_guideline = implement_career_guideline.replace('0', "'Thu ng??n'") \
                    .replace('1', "'C???a h??ng tr?????ng'")
        else:
            new_store_image = sale_report.new_store_image
            image_outside = sale_report.image_outside_v2
            image_inside = sale_report.image_inside_v2
            image_store_cashier = sale_report.image_store_cashier_v2
            cessation_of_business_image = sale_report.cessation_of_business_image_v2
            posm = sale_report.posm_v2
            implement_merchant_view = sale_report.implement_merchant_view
            implement_career_guideline = sale_report.implement_career_guideline
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
                'new_note': sale_report.new_note,

            },
            'shop': {
                'shop_id': shop.id if sale_report.shop_code else 0,
                'shop_address': shop.address if sale_report.shop_code else '',
                'shop_code': sale_report.shop_code if sale_report.shop_code else '',
                'shop_name': shop.name if sale_report.shop_code else '',
                'merchant_name': shop.merchant.merchant_name if sale_report.shop_code else '',
                'merchant_code': shop.merchant.merchant_code if sale_report.shop_code else '',
                'merchant_brand': shop.merchant.merchant_brand if sale_report.shop_code else '',
            },
            'shop_status': sale_report.shop_status,
            'new_store_image': str(new_store_image),
            'image_outside': image_outside,
            'image_inside': image_inside,
            'image_store_cashier': image_store_cashier,
            'posm': posm,

            # ngh??? kinh doanh
            'cessation_of_business_note': sale_report.cessation_of_business_note,
            'cessation_of_business_image': cessation_of_business_image,

            # ch??m s??c
            'customer_care_cashier_reward': sale_report.customer_care_cashier_reward,
            'customer_care_transaction': sale_report.customer_care_transaction,

            # tri???n khai
            'implement_merchant_view': implement_merchant_view,
            'implement_career_guideline': implement_career_guideline,
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

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('sale_report_form.report_statistic_list_data',
                                                             self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
            API get SaleReportStatisticView   \n
            param c?? report_date report_month team_id
        """
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        team_id = self.request.query_params.get('team_id', None)
        staff_id = self.request.query_params.get('staff_id', None)

        raw_query = get_raw_query_statistic(user=self.request.user, from_date=from_date, to_date=to_date,
                                            team_id=team_id, staff_id=staff_id)
        queryset = SaleReport.objects.raw(raw_query)
        return queryset


def get_list_queryset(request):
    purpose = request.query_params.get('purpose', None)
    shop_id = request.query_params.get('shop_id', None)
    staff_id = request.query_params.get('staff_id', None)
    team_id = request.query_params.get('team_id', None)
    from_date = request.query_params.get('from_date', None)
    to_date = request.query_params.get('to_date', None)

    queryset = SaleReport.objects.filter(is_draft=False) \
        .filter(created_by__in=get_users_viewable_queryset(request.user))

    if purpose is not None and purpose != '':
        queryset = queryset.filter(purpose=purpose)

    if shop_id is not None and shop_id != '':
        shop_id = format_string(shop_id)
        queryset = queryset.filter(shop_code=shop_id)

    if staff_id is not None and staff_id != '':
        staff = Staff.objects.filter(pk=staff_id).first()
        users = User.objects.filter(email=staff.email)
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


def get_raw_query_statistic(user=None, from_date=None, to_date=None, team_id=None, staff_id=None):
    filter_time = ''

    if (from_date is None or from_date == '') and (to_date is None or to_date == ''):
        filter_time += "and created_date >= '" + \
                       dt_datetime.now().strftime('%Y-%m-%d') + ' 00:00:00' + "'"
    else:
        if from_date is not None and from_date != '':
            filter_time += "and created_date >= '" + \
                           dt_datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S') + "'"

        if to_date is not None and to_date == '':
            filter_time += "and created_date <= '" + \
                           dt_datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59' + "'"

    users = get_users_viewable_queryset(user)
    if team_id is not None and team_id != '':
        staffs = Staff.objects.all().filter(team_id=team_id)
        staff_emails = [x.email for x in staffs]
        users = users.filter(email__in=staff_emails)

    users_id = [x.id for x in users]
    if staff_id is not None and staff_id != '':
        staff = Staff.objects.filter(pk=staff_id).first()
        user = User.objects.filter(email=staff.email)[0]
        if user.id in users_id:
            users_id = [user.id]
        else:
            users_id = []
    filter_user = 'and created_by_id in {}'.format(tuple(users_id)) if len(users_id) > 0 else 'and false'
    if filter_user.endswith(",)"):
        filter_user = filter_user[:-2] + ")"
    elif filter_user.endswith(", )"):
        filter_user = filter_user[:-3] + ")"

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
@permission_required('sale_report_form.get_list_draft_report', raise_exception=True)
def list_draff(request):
    """
        API get list_draff   \n
        tr??? v??? danh s??ch t??n c??c b???n nh??p \n
        param c?? name , l?? chu???i k?? t??? ????? search
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
@permission_required('sale_report_form.report_statistic__export_data', raise_exception=True)
@login_required
def report_statistic_export_data(request):
    """
        API get export statistic view to excel   \n
        param bao g???m  date, month, team_id \n
        v?? option l?? m???t string array ???? ???????c convert sang json string, bao g???m c??c tr?????ng mu???n export v?? d??? \n
        \t ["full_name","email","count_total","count_new","count_standee_ctkm","count_standee_qr","count_new_refused"] \n
        n???u options l?? null, s??? export to??n b??? c??c tr?????ng : \n
        \t ["full_name","email","count_total","count_new","count_impl", \n
        \t "count_care","count_new_signed","count_new_unsigned", \n
        \t "count_new_consider","count_new_refused","count_care_cessation", \n
        \t "count_care_liquidation","count_care_opening","count_care_uncooperative", \n
        \t "count_standee_qr","count_sticker_door","count_sticker_table","count_guide", \n
        \t "count_wobbler","count_poster","count_standee_ctkm","count_tentcard"]\n
    """
    full_options = ['full_name', 'email', 'count_total', 'count_care', 'count_impl',

                    'count_new', 'count_new_signed', 'count_new_unsigned',

                    'count_new_consider', 'count_new_refused', 'count_care_cessation',

                    'count_care_liquidation', 'count_care_opening', 'count_care_uncooperative',

                    'count_standee_qr', 'count_sticker_door', 'count_sticker_table', 'count_guide',

                    'count_wobbler', 'count_poster', 'count_standee_ctkm', 'count_tentcard']
    post_options = request.GET.get('options', None)
    try:
        post_options = ast.literal_eval(post_options)
    except Exception as e:
        post_options = []
    if len(post_options) == 0:
        options = full_options
    else:
        options = []
        for op in full_options:
            if op in post_options:
                options.append(op)
    check_or_create_excel_folder()

    if not os.path.exists(settings.MEDIA_ROOT + '/excel/sale-report-statistic'):
        os.mkdir(os.path.join(settings.MEDIA_ROOT + '/excel', 'sale-report-statistic'))

    file_name = 'sale_report_statistic_' + str(int(time_t.time())) + '.xlsx'
    workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + '/excel/sale-report-statistic/' + file_name)
    worksheet = workbook.add_worksheet('TH???NG K?? HO???T ?????NG SALE')

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
    start = 65
    if 'full_name' in options:
        worksheet.merge_range(str(chr(start)) + '1' + ':' + str(chr(start)) + '2', 'Nh??n vi??n', merge_format)
        start = start + 1
    if 'email' in options:
        worksheet.merge_range(str(chr(start)) + '1' + ':' + str(chr(start)) + '2', 'Gmail', merge_format)
        start = start + 1

    start_total = start
    if 'count_total' in options:
        worksheet.write(str(chr(start)) + '2', 'T???ng', merge_format)
        start = start + 1
    if 'count_care' in options:
        worksheet.write(str(chr(start)) + '2', 'S??? MC ch??m s??c', merge_format)
        start = start + 1
    if 'count_impl' in options:
        worksheet.write(str(chr(start)) + '2', 'S??? MC tri???n khai', merge_format)
        start = start + 1
    if 'count_new' in options:
        worksheet.write(str(chr(start)) + '2', 'S??? MC ti???p c???n m??? m???i', merge_format)
        start = start + 1
    end_total = start - 1
    if 'count_total' in options or 'count_care' in options or 'count_impl' in options or 'count_new' in options:
        if end_total - start_total > 0:
            worksheet.merge_range(str(chr(start_total)) + '1' + ':' + str(chr(end_total)) + '1',
                                  'T???ng s??? l???n ti???p x??c',
                                  merge_format)
        else:
            worksheet.write(str(chr(start_total)) + '1', 'T???ng s??? l???n ti???p x??c', merge_format)

    start_new = start
    if 'count_new_signed' in options:
        worksheet.write(str(chr(start)) + '2', '?????ng ??, ???? k?? H??', merge_format)
        start = start + 1
    if 'count_new_unsigned' in options:
        worksheet.write(str(chr(start)) + '2', '?????ng ??, ch??a k?? H??', merge_format)
        start = start + 1
    if 'count_new_consider' in options:
        worksheet.write(str(chr(start)) + '2', 'C???n xem x??t', merge_format)
        start = start + 1
    if 'count_new_refused' in options:
        worksheet.write(str(chr(start)) + '2', 'T??? ch???i h???p t??c', merge_format)
        start = start + 1
    end_new = start - 1
    if 'count_new_signed' in options or 'count_new_unsigned' in options or 'count_new_consider' in options or 'count_new_refused' in options:
        if end_new - start_new > 0:
            worksheet.merge_range(str(chr(start_new)) + '1' + ':' + str(chr(end_new)) + '1',
                                  'K???t qu??? m??? m???i',
                                  merge_format)
        else:
            worksheet.write(str(chr(start_new)) + '1', 'K???t qu??? m??? m???i', merge_format)

    start_care = start
    if 'count_care_cessation' in options:
        worksheet.write(str(chr(start)) + '2', '???? ngh??? kinh doanh', merge_format)
        start = start + 1
    if 'count_care_liquidation' in options:
        worksheet.write(str(chr(start)) + '2', 'Mu???n thanh l?? QR', merge_format)
        start = start + 1
    if 'count_care_opening' in options:
        worksheet.write(str(chr(start)) + '2', '??ang ho???t ?????ng', merge_format)
        start = start + 1
    if 'count_care_uncooperative' in options:
        worksheet.write(str(chr(start)) + '2', 'Kh??ng h???p t??c', merge_format)
        start = start + 1
    end_care = start - 1
    if 'count_care_cessation' in options or 'count_care_liquidation' in options or 'count_care_opening' in options or 'count_care_uncooperative' in options:
        if end_care - start_care > 0:
            worksheet.merge_range(str(chr(start_care)) + '1' + ':' + str(chr(end_care)) + '1',
                                  'K???t qu??? ch??m s??c',
                                  merge_format)
        else:
            worksheet.write(str(chr(start_care)) + '1', 'K???t qu??? ch??m s??c', merge_format)
    start_pub = start
    if 'count_standee_qr' in options:
        worksheet.write(str(chr(start)) + '2', 'Standee m?? QR', merge_format)
        start = start + 1
    if 'count_sticker_door' in options:
        worksheet.write(str(chr(start)) + '2', 'Sticker d??n c???a', merge_format)
        start = start + 1
    if 'count_sticker_table' in options:
        worksheet.write(str(chr(start)) + '2', 'Sticker d??n b??n thu ng??n', merge_format)
        start = start + 1
    if 'count_guide' in options:
        worksheet.write(str(chr(start)) + '2', 'H?????ng d???n SD', merge_format)
        start = start + 1
    if 'count_wobbler' in options:
        worksheet.write(str(chr(start)) + '2', 'Wobbler CTKM', merge_format)
        start = start + 1
    if 'count_poster' in options:
        worksheet.write(str(chr(start)) + '2', 'Poster CTKM', merge_format)
        start = start + 1
    if 'count_standee_ctkm' in options:
        worksheet.write(str(chr(start)) + '2', 'Standee CTKM (60x160)', merge_format)
        start = start + 1
    if 'count_tentcard' in options:
        worksheet.write(str(chr(start)) + '2', 'Tentcard CTKM', merge_format)
        start = start + 1
    end_pub = start - 1
    if 'count_standee_qr' in options or 'count_sticker_door' in options or 'count_sticker_table' in options or 'count_guide' in options \
            or 'count_wobbler' in options or 'count_poster' in options or 'count_standee_ctkm' in options or 'count_tentcard' in options:
        if end_pub - start_pub > 0:
            worksheet.merge_range(str(chr(start_pub)) + '1' + ':' + str(chr(end_pub)) + '1',
                                  'S??? l?????ng ???n ph???m s??? d???ng',
                                  merge_format)
        else:
            worksheet.write(str(chr(start_pub)) + '1', 'S??? l?????ng ???n ph???m s??? d???ng', merge_format)

    worksheet.freeze_panes(2, 0)

    data = get_statistic_data(request)

    row_num = 2
    for item in data:
        for index, op in enumerate(options):
            worksheet.write(row_num, index, getattr(item, op))
        row_num += 1

    workbook.close()

    return JsonResponse({
        'status': 200,
        'data': settings.MEDIA_URL + '/excel/sale-report-statistic/' + file_name},
        status=200
    )


@api_view(['GET'])
@permission_required('sale_report_form.report_list_export_data', raise_exception=True)
@login_required
def report_list_export_data(request):
    check_or_create_excel_folder()

    if not os.path.exists(settings.MEDIA_ROOT + '/excel/sale-report'):
        os.mkdir(os.path.join(settings.MEDIA_ROOT + '/excel', 'sale-report'))

    file_name = 'sale-report_' + str(int(time_f())) + '.xlsx'
    workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + '/excel/sale-report/' + file_name)
    worksheet = workbook.add_worksheet('DANH S??CH TI???P C???N MERCHANT')

    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#74beff',
        'font_color': '#ffffff',
    })

    worksheet.write('A1', 'M???c ????ch', merge_format)
    worksheet.write('B1', 'Merchant Brand', merge_format)
    worksheet.write('C1', 'C???a h??ng', merge_format)
    worksheet.write('D1', 'Ng??y t???o', merge_format)
    worksheet.write('E1', 'Nh??n vi??n t???o', merge_format)
    worksheet.write('F1', 'Team', merge_format)

    worksheet.freeze_panes(1, 0)

    list_id = get_list_queryset(request)
    filter_id = ''
    for sr in list_id:
        filter_id = filter_id + ',' + str(sr.id)

    date = []
    if filter_id.startswith(','):
        filter_id = filter_id[1:]
        raw_query = '''
        SELECT srf.id, srf.purpose,
        ( CASE WHEN srf.purpose=0 THEN srf.new_merchant_name ELSE mc.merchant_code||' - '|| mc.merchant_brand END) AS merchant_name, 
        sh.code,srf.created_date, st.email, tm.name
        from sale_report_form srf
        LEFT JOIN shop sh on srf.shop_code= sh.code
        LEFT JOIN merchant mc on sh.merchant_id= mc.id
        LEFT JOIN auth_user au on srf.created_by_id= au.id
        LEFT JOIN staff st on au.email = st.email
        LEFT JOIN team tm on st.team_id= tm.id
        WHERE au.email IS NOT NULL AND au.email!=''  AND srf.id IN (%s) 
        ORDER BY srf.created_date DESC
        ''' % (filter_id)
        with connection.cursor() as cursor:
            cursor.execute(raw_query)
            columns = [col[0] for col in cursor.description]
            data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

    row_num = 1

    for item in data:
        switcher = {
            0: 'M??? m???i',
            1: 'Tri???n khai',
            2: 'Ch??m s??c',
        }
        worksheet.write(row_num, 0, switcher.get(item['purpose'], "Other"))
        worksheet.write(row_num, 1, item['merchant_name'])
        worksheet.write(row_num, 2, item['code'])
        worksheet.write(row_num, 3, formats.date_format(item['created_date'], "SHORT_DATETIME_FORMAT") \
            if item['created_date'] else '')
        worksheet.write(row_num, 4, item['email'])
        worksheet.write(row_num, 5, item['name'])
        row_num += 1

    workbook.close()
    return successful_response(settings.MEDIA_URL + 'excel/sale-report/' + file_name)


def get_statistic_data(request):
    from_date = request.query_params.get('from_date', None)
    to_date = request.query_params.get('to_date', None)
    team_id = request.GET.get('team_id', None)
    staff_id = request.query_params.get('staff_id', None)

    raw_query = get_raw_query_statistic(request.user, from_date=from_date, to_date=to_date,
                                        team_id=team_id, staff_id=staff_id)

    if raw_query == '':
        return []
    else:
        return SaleReport.objects.raw(raw_query)


@api_view(['GET'])
@login_required
@permission_required('sale_report_form.dashboard_sale_report_form_count', raise_exception=True)
def count_sale_report_form_14_days_before_heatmap(request):
    today = date.today()
    date_list = []
    hour_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    for i in range(0, 14):
        date_list.append((today - timedelta(days=14) + timedelta(days=i)).strftime("%d/%m/%Y"))

    with connection.cursor() as cursor:
        cursor.execute('''
            select count(*),
                   date(created_date)              as sale_report_form_date,
                   extract(hour from created_date) as sale_report_form_hour
            from sale_report_form
            where created_date > current_date - interval '14 days'
              and created_date < current_date
            group by sale_report_form_date, sale_report_form_hour
            order by sale_report_form_date asc
        ''')
        columns = [col[0] for col in cursor.description]
        data_cursor = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    data = []
    for item in data_cursor:
        data.append([
            date_list.index(str(item['sale_report_form_date'].strftime("%d/%m/%Y"))),
            hour_list.index(item['sale_report_form_hour']),
            item['count']
        ])

    return successful_response({
        'data': data,
        'date_list': date_list,
        'hour_list': hour_list
    })
