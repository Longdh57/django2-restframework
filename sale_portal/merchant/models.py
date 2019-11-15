from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from sale_portal.merchant import MerchantLogType
from ..staff.models import Staff
from ..shop_cube.models import ShopCube
from ..qr_status.models import QrStatus


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
    merchant_type = models.IntegerField(null=True,help_text='Equivalent with qr_merchant.merchant_type')
    address = models.CharField(max_length=150, null=True, help_text='Equivalent with qr_merchant.address')
    description = models.CharField(max_length=100, null=True, help_text='Equivalent with qr_merchant.description')
    status = models.IntegerField(default=1, null=True, help_text='Equivalent with qr_merchant.status')
    department = models.IntegerField(null=True, help_text='Equivalent with qr_merchant.department')
    staff = models.IntegerField(null=True, help_text='Equivalent with qr_merchant.staff')
    created_date = models.DateTimeField(null=True, help_text='Equivalent with qr_merchant.created_date')
    modify_date = models.DateTimeField(null=True, help_text='Equivalent with qr_merchant.modify_date')
    is_care = models.IntegerField(default=1)
    un_care_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'merchant'
        default_permissions = ()

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
        return Staff.objects.filter(pk=self.staff).first()

    def get_type(self):
        return QrTypeMerchant.objects.filter(id=self.merchant_type).first()

    def get_status(self):
        status = QrStatus.objects.filter(type='MERCHANT', code=self.status).first()
        if status is None:
            return '<span class="badge badge-dark">Khác</span>'
        switcher = {
            -1: '<span class="badge badge-danger">' + status.description + '</span>',
            1: '<span class="badge badge-success">' + status.description + '</span>',
            2: '<span class="badge badge-secondary">' + status.description + '</span>',
            3: '<span class="badge badge-warning">' + status.description + '</span>',
            4: '<span class="badge badge-primary">' + status.description + '</span>',
            5: '<span class="badge badge-danger">' + status.description + '</span>',
            6: '<span class="badge badge-danger">' + status.description + '</span>'
        }
        return switcher.get(status.code, '<span class="badge badge-dark">Khác</span>')

    def get_merchant_cube(self):
        shops = self.shops.values('id')
        shop_cubes = ShopCube.objects.filter(shop_id__in=shops)
        merchant_cube = {
            'number_of_tran_7d': 0,
            'number_of_tran_acm': 0,
            'value_of_tran_7d': 0,
            'value_of_tran_acm': 0,
            'number_of_new_customer': 0,
            'number_of_tran': 0,
            'value_of_tran': 0,
            'number_of_tran_30d': 0
        }
        for shop_cube in shop_cubes:
            merchant_cube.update(
                number_of_tran_7d=merchant_cube.get('number_of_tran_7d') + shop_cube.number_of_tran_7d,
                number_of_tran_acm=merchant_cube.get('number_of_tran_acm') + shop_cube.number_of_tran_acm,
                value_of_tran_7d=merchant_cube.get('value_of_tran_7d') + int(shop_cube.value_of_tran_7d),
                value_of_tran_acm=merchant_cube.get('value_of_tran_acm') + int(shop_cube.value_of_tran_acm),
                number_of_new_customer=merchant_cube.get('number_of_new_customer') + int(
                    shop_cube.number_of_new_customer),
                number_of_tran=merchant_cube.get('number_of_tran') + int(shop_cube.number_of_tran),
                value_of_tran=merchant_cube.get('value_of_tran') + int(shop_cube.value_of_tran),
                number_of_tran_30d=merchant_cube.get('number_of_tran_30d') + int(shop_cube.number_of_tran_30d),
            )
        return merchant_cube


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
