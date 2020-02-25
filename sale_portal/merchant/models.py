import logging

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from sale_portal.merchant import MerchantLogType
from sale_portal.staff_care import StaffCareType
from sale_portal.shop_cube.models import ShopCube
from sale_portal.qr_status.models import QrStatus
from sale_portal.staff.models import Staff, QrStaff
from sale_portal.administrative_unit.models import QrProvince


class QrMerchant(models.Model):
    merchant_code = models.TextField(null=True)
    service_code = models.TextField(null=True)
    merchant_brand = models.TextField(null=True)
    merchant_name = models.TextField(null=True)
    merchant_type = models.IntegerField(null=True)
    address = models.TextField(null=True)
    description = models.TextField(null=True)
    status = models.IntegerField(default=1, null=True)
    website = models.TextField(null=True)
    master_merchant_code = models.TextField(null=True)
    province_code = models.CharField(max_length=10, null=True)
    district_code = models.CharField(max_length=10, null=True)
    department = models.IntegerField(null=True)
    staff = models.IntegerField(null=True)
    genqr_checksum = models.IntegerField(null=True)
    genqr_accesskey = models.TextField(null=True)
    switch_code = models.IntegerField(default=1)
    created_date = models.DateTimeField(null=True)
    modify_date = models.DateTimeField(null=True)
    process_user = models.TextField(null=True)
    denied_approve_desc = models.TextField(null=True)
    create_user = models.TextField(null=True)
    org_status = models.IntegerField(null=True)
    email_vnpay = models.TextField(null=True)
    pass_email_vnpay = models.TextField(null=True)
    process_addition = models.TextField(null=True)
    denied_approve_code = models.IntegerField(default=0)
    business_address = models.TextField(null=True)
    app_user = models.TextField(null=True)
    pin_code = models.TextField(null=True)
    provider_code = models.TextField(null=True)
    wards_code = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = 'qr_merchant'
        ordering = ['-created_date']
        default_permissions = ()

    def __str__(self):
        return self.merchant_code


class QrMerchantInfo(models.Model):
    merchant_code = models.TextField(null=True)
    rm_auth = models.DecimalField(blank=True, null=True, max_digits=38, decimal_places=0)
    register_sms = models.DecimalField(blank=True, null=True, max_digits=38, decimal_places=0)
    register_ott = models.DecimalField(blank=True, null=True, max_digits=38, decimal_places=0)
    to_create_user = models.DecimalField(blank=True, null=True, max_digits=38, decimal_places=0)
    to_merchant = models.DecimalField(blank=True, null=True, max_digits=38, decimal_places=0)
    receive_phone = models.TextField(null=True)
    receive_email = models.TextField(null=True)
    contact_name = models.TextField(null=True)
    contact_phone = models.TextField(null=True)
    contact_email = models.TextField(null=True)
    contact_phone1 = models.TextField(null=True)
    contact_phone2 = models.TextField(null=True)
    contact_email1 = models.TextField(null=True)
    contact_email2 = models.TextField(null=True)

    class Meta:
        db_table = 'qr_merchant_info'
        default_permissions = ()


class QrTypeMerchant(models.Model):
    id = models.IntegerField(primary_key=True)
    type_code = models.CharField(max_length=150, null=True)
    brand_name = models.CharField(max_length=150, null=True)
    full_name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    created_date = models.DateTimeField(null=True)
    updated_date = models.DateTimeField(null=True)
    status = models.IntegerField(default=1, null=True)

    class Meta:
        db_table = 'qr_type_merchant'
        ordering = ['-created_date']
        default_permissions = ()

    def __str__(self):
        return self.type_code


class Merchant(models.Model):
    merchant_code = models.CharField(max_length=20, null=True, help_text='Equivalent with qr_merchant.merchant_code')
    merchant_brand = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_merchant.merchant_brand')
    merchant_name = models.CharField(max_length=100, null=True, help_text='Equivalent with qr_merchant.merchant_name')
    merchant_type = models.IntegerField(null=True, help_text='Equivalent with qr_merchant.merchant_type')
    address = models.CharField(max_length=150, null=True, help_text='Equivalent with qr_merchant.address')
    description = models.CharField(max_length=100, null=True, help_text='Equivalent with qr_merchant.description')
    status = models.IntegerField(default=1, null=True, help_text='Equivalent with qr_merchant.status')
    department = models.IntegerField(null=True, help_text='Equivalent with qr_merchant.department')
    staff = models.IntegerField(null=True, help_text='Equivalent with qr_merchant.staff')
    created_date = models.DateTimeField(null=True, help_text='Equivalent with qr_merchant.created_date')
    modify_date = models.DateTimeField(null=True, help_text='Equivalent with qr_merchant.modify_date')
    province_code = models.CharField(max_length=10, null=True, help_text='Equivalent with qr_terminal.province_code')
    district_code = models.CharField(max_length=10, null=True, help_text='Equivalent with qr_terminal.district_code')
    wards_code = models.CharField(max_length=10, null=True, help_text='Equivalent with qr_terminal.wards_code')
    is_care = models.IntegerField(default=1)
    un_care_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'merchant'
        ordering = ['-created_date']
        default_permissions = ()
        permissions = (
            ('merchant_list_data', 'Can get merchant list data'),
            ('merchant_detail', 'Can get merchant detail'),
        )

    def __str__(self):
        return self.merchant_code

    def get_qr_merchant(self):
        try:
            qr_merchant = QrMerchant.objects.get(pk=self.pk)
        except QrMerchant.DoesNotExist:
            qr_merchant = None
        return qr_merchant

    def change_is_care(self):
        if self.is_care == 1:
            self.is_take_care = 0
            self.un_care_date = timezone.now()
            self.save()
        else:
            self.is_take_care = 1
            self.un_care_date = None
            self.save()
        return

    def get_staff(self):
        try:
            qr_staff = QrStaff.objects.filter(staff_id=self.staff).first()
            if qr_staff is None:
                return None
            staff = Staff.objects.filter(email=qr_staff.email).first()
            return staff
        except Exception as e:
            logging.ERROR("Exception merchant model get_staff: {}".format(e))
            return None

    @property
    def province(self):
        province = QrProvince.objects.filter(province_code=self.province_code).first()
        if province is not None:
            return province
        return None

    @property
    def staff_care(self):
        staff_care = self.staff_cares.filter(type=StaffCareType.STAFF_MERCHANT).first()
        if staff_care is not None:
            return staff_care.staff
        return None

    @property
    def team_care(self):
        staff_care = self.staff_cares.filter(type=StaffCareType.STAFF_MERCHANT).first()
        if staff_care is not None:
            return staff_care.staff.team
        return None

    def staff_create(self, staff_id, request=None):
        staff_care = self.staff_cares.filter(type=StaffCareType.STAFF_MERCHANT).first()
        if staff_care is None:
            try:
                staff_care = self.staff_cares.create(
                    staff_id=staff_id,
                    shop_id=None,
                    type=StaffCareType.STAFF_MERCHANT
                )
                create_staff_care_log(merchant=self, staff_id=staff_id, type=StaffCareType.STAFF_MERCHANT,
                                      request=request)
                return staff_care.staff
            except Exception as e:
                logging.error('Create staff-merchant exception: %s', e)
        else:
            raise Exception('Merchant already exist a staff ')

    def staff_delete(self, request=None):
        try:
            remove_staff_care(merchant=self, type=StaffCareType.STAFF_MERCHANT, request=request)
        except Exception as e:
            logging.error('Delete staff-merchant exception: %s', e)

    def get_type(self):
        return QrTypeMerchant.objects.filter(id=self.merchant_type).first()

    def get_status(self):
        status = QrStatus.objects.filter(type='MERCHANT', code=self.status).first()
        return status.code if status else None

    def get_merchant_cube(self):
        shops = self.shops.values('id')
        shop_cubes = ShopCube.objects.filter(shop_id__in=shops)

        number_of_tran = 0
        number_of_tran_w_1_7 = 0
        number_of_tran_w_8_14 = 0
        number_of_tran_w_15_21 = 0
        number_of_tran_w_22_end = 0

        for shop_cube in shop_cubes:
            if shop_cube.number_of_tran:
                number_of_tran = number_of_tran + int(shop_cube.number_of_tran)
            if shop_cube.number_of_tran_w_1_7:
                number_of_tran_w_1_7 = number_of_tran_w_1_7 + int(shop_cube.number_of_tran_w_1_7)
            if shop_cube.number_of_tran_w_8_14:
                number_of_tran_w_8_14 = number_of_tran_w_8_14 + int(shop_cube.number_of_tran_w_8_14)
            if shop_cube.number_of_tran_w_15_21:
                number_of_tran_w_15_21 = number_of_tran_w_15_21 + int(shop_cube.number_of_tran_w_15_21)
            if shop_cube.number_of_tran_w_22_end:
                number_of_tran_w_22_end = number_of_tran_w_22_end + int(shop_cube.number_of_tran_w_22_end)

        merchant_cube = {
            'number_of_tran': number_of_tran if number_of_tran < 6 else 5,
            'number_of_tran_w_1_7': number_of_tran_w_1_7 if number_of_tran_w_1_7 < 6 else 5,
            'number_of_tran_w_8_14': number_of_tran_w_8_14 if number_of_tran_w_8_14 < 6 else 5,
            'number_of_tran_w_15_21': number_of_tran_w_15_21 if number_of_tran_w_15_21 < 6 else 5,
            'number_of_tran_w_22_end': number_of_tran_w_22_end if number_of_tran_w_22_end < 6 else 5,
        }
        return merchant_cube


def create_staff_care_log(merchant, staff_id, type, request):
    merchant.staff_care_logs.create(
        staff_id=staff_id,
        merchant_id=merchant.id,
        type=type,
        is_caring=True,
        created_by=request.user if request else None,
        updated_by=request.user if request else None
    )


def remove_staff_care(merchant, type, request):
    merchant_id = merchant.id

    staff_care = merchant.staff_cares.filter(type=type).first()

    staff = staff_care.staff

    staff_care.delete()

    if staff_care is not None:
        staff_care_log = merchant.staff_care_logs.filter(staff=staff, type=type, is_caring=True).order_by('id').first()
        if staff_care_log is not None:
            staff_care_log.is_caring = False
            staff_care_log.updated_by_id = request.user.id if request else None
            staff_care_log.save()
        else:
            merchant.staff_care_logs.create(
                staff_id=staff.id,
                merchant_id=merchant_id,
                type=type,
                is_caring=False,
                created_by=request.user if request else None,
                updated_by=request.user if request else None
            )


class MerchantLog(models.Model):
    old_data = JSONField(blank=True, default=dict)
    new_data = JSONField(blank=True, default=dict)
    type = models.IntegerField(choices=MerchantLogType.CHOICES)
    merchant_id = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'merchant_log'
        default_permissions = ()

    def get_new_data(self):
        return self.new_data
