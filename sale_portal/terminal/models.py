import logging

from django.db import models
from django.contrib.postgres.fields import JSONField

from sale_portal.shop.models import Shop
from sale_portal.merchant.models import Merchant
from sale_portal.terminal import TerminalLogType
from ..qr_status.models import QrStatus
from ..administrative_unit.models import QrProvince, QrDistrict, QrWards


class QrTerminal(models.Model):
    terminal_id = models.TextField(null=True)
    merchant_id = models.IntegerField(null=True)
    terminal_name = models.TextField(null=True)
    terminal_address = models.TextField(null=True)
    tax_code = models.TextField(max_length=15, null=True)
    website = models.TextField(null=True)
    website_business = models.TextField(null=True)
    facebook = models.TextField(null=True)
    business_product = models.IntegerField(null=True)
    product_description = models.TextField(null=True)
    register_qr = models.IntegerField(null=True)
    register_vnpayment = models.IntegerField(null=True)
    account_id = models.IntegerField(null=True)
    account_vnmart_id = models.IntegerField(null=True)
    status = models.IntegerField(null=True)
    created_date = models.DateTimeField(null=True)
    modify_date = models.DateTimeField(null=True)
    the_first = models.IntegerField(null=True)
    process_user = models.TextField(null=True)
    denied_approve_desc = models.TextField(null=True)
    process_addition = models.TextField(null=True)
    user_lock = models.TextField(null=True)
    denied_approve_code = models.IntegerField(null=True)
    business_address = models.TextField(null=True)
    register_sms = models.IntegerField(null=True)
    register_ott = models.IntegerField(null=True)
    terminal_app_user = models.TextField(null=True)
    terminal_document = models.TextField(null=True)
    service_code = models.TextField(null=True)
    create_user = models.TextField(null=True)
    visa_pan = models.TextField(null=True)
    master_pan = models.TextField(null=True)
    unionpay_pan = models.TextField(null=True)
    file_name = models.TextField(null=True)
    province_code = models.CharField(max_length=10, null=True)
    district_code = models.CharField(max_length=10, null=True)
    wards_code = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = 'qr_terminal'
        ordering = ['-created_date']
        default_permissions = ()

    def __str__(self):
        return self.terminal_name


class QrTerminalContact(models.Model):
    merchant_code = models.CharField(max_length=255, null=True, blank=True)
    terminal_id = models.CharField(max_length=255, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    phone1 = models.CharField(max_length=255, null=True, blank=True)
    phone2 = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    email1 = models.CharField(max_length=255, null=True, blank=True)
    email2 = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    create_terminal_app = models.DecimalField(blank=True, null=True, max_digits=38, decimal_places=0)
    to_create_user = models.DecimalField(blank=True, null=True, max_digits=38, decimal_places=0)
    to_terminal = models.DecimalField(blank=True, null=True, max_digits=38, decimal_places=0)
    receive_phone = models.CharField(max_length=255, null=True, blank=True)
    receive_mail = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'qr_terminal_contact'
        default_permissions = ()

    def __str__(self):
        return self.terminal_id


class TerminalQueryset(models.QuerySet):
    def terminal_register_vnpayment(self):
        """Return register_vnpayment terminals."""
        return self.filter(register_vnpayment=1)

    def terminal_un_register_vnpayment(self):
        """Return un register_vnpayment terminals."""
        return self.exclude(register_vnpayment=1)


class Terminal(models.Model):
    terminal_id = models.CharField(max_length=100, null=True, help_text='Equivalent with qr_terminal.terminal_id')
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.SET_NULL,
        related_name="terminals",
        blank=True,
        null=True,
        help_text='Equivalent with qr_terminal.merchant_id'
    )
    terminal_name = models.CharField(max_length=100, null=True, help_text='Equivalent with qr_terminal.terminal_name')
    terminal_address = models.CharField(max_length=255, null=True,
                                        help_text='Equivalent with qr_terminal.terminal_address')
    register_qr = models.IntegerField(null=True, help_text='Equivalent with qr_terminal.register_qr')
    register_vnpayment = models.IntegerField(null=True, help_text='Equivalent with qr_terminal.register_vnpayment')
    status = models.IntegerField(null=True, help_text='Equivalent with qr_terminal.status')
    province_code = models.CharField(max_length=10, null=True, help_text='Equivalent with qr_terminal.province_code')
    district_code = models.CharField(max_length=10, null=True, help_text='Equivalent with qr_terminal.district_code')
    wards_code = models.CharField(max_length=10, null=True, help_text='Equivalent with qr_terminal.wards_code')
    business_address = models.CharField(max_length=255, null=True,
                                        help_text='Equivalent with qr_terminal.business_address')
    created_date = models.DateTimeField(null=True, help_text='Equivalent with qr_terminal.created_date')
    modify_date = models.DateTimeField(null=True, help_text='Equivalent with qr_terminal.modify_date')
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, related_name='terminals', blank=True, null=True)

    objects = TerminalQueryset.as_manager()

    class Meta:
        db_table = 'terminal'
        ordering = ['-created_date']
        default_permissions = ()

    def __str__(self):
        return self.terminal_id

    def __init__(self, *args, **kwargs):
        super(Terminal, self).__init__(*args, **kwargs)
        self.__important_fields = ['shop_id']
        for field in self.__important_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def compare(self):
        old_data = {}
        new_data = {}
        log_type = TerminalLogType.CREATE_NEW

        for field in self.__important_fields:
            orig = '__original_%s' % field
            old_data[field] = getattr(self, field)
            new_data[field] = getattr(self, orig)
            if field == 'shop_id' and getattr(self, orig) != getattr(self, field):
                log_type = TerminalLogType.CHANGE_SHOP
        return old_data, new_data, log_type

    def save(self, *args, **kwargs):
        try:
            old_data, new_data, type = self.compare()
            if type == TerminalLogType.CHANGE_SHOP:
                TerminalLog.objects.create(old_data=old_data, new_data=new_data, terminal_id=self.id, type=type)
        except Exception as e:
            logging.error('Save terminal exception: %s', e)
        super(Terminal, self).save(*args, **kwargs)

    def get_qr_terminal(self):
        try:
            qr_terminal = QrTerminal.objects.get(pk=self.pk)
        except QrTerminal.DoesNotExist:
            qr_terminal = None
        return qr_terminal

    def get_qr_terminal_contact(self):
        try:
            qr_terminal_contact = QrTerminalContact.objects.filter(terminal_id=self.terminal_id).first()
        except QrTerminalContact.DoesNotExist:
            qr_terminal_contact = None
        return qr_terminal_contact

    def get_status(self):
        status = QrStatus.objects.filter(type='TERMINAL', code=self.status).first()
        return status.code if status else None

    def get_staff(self):
        return self.shop.staff if self.shop else None

    def get_team(self):
        return self.shop.staff.team if self.shop and self.shop.staff else None

    def get_province(self):
        try:
            qr_province = QrProvince.objects.filter(province_code=self.province_code).first()
        except QrProvince.DoesNotExist:
            qr_province = None
        return qr_province

    def get_district(self):
        try:
            qr_district = QrDistrict.objects.filter(district_code=self.district_code).first()
        except QrDistrict.DoesNotExist:
            qr_district = None
        return qr_district

    def get_wards(self):
        try:
            qr_wards = QrWards.objects.filter(wards_code=self.wards_code).first()
        except QrWards.DoesNotExist:
            qr_wards = None
        return qr_wards


class TerminalLog(models.Model):
    old_data = JSONField(blank=True, default=dict)
    new_data = JSONField(blank=True, default=dict)
    type = models.IntegerField(choices=TerminalLogType.CHOICES)
    terminal_id = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'terminal_log'
        default_permissions = ()

    def get_new_data(self):
        return self.new_data
