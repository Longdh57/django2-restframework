from django.db import models

from sale_portal.user.models import User
from sale_portal.shop.models import Shop
from sale_portal.staff.models import Staff
from sale_portal.sale_report_form import SaleReportFormPurposeTypes, SaleReportFormCreateNewResults, \
    SaleReportFormNewUsingApplications, SaleReportFormShopStatus, SaleReportFormShopConfirm, SaleReportFormCashierReward


class SaleReport(models.Model):
    # Thong tin chung
    # Muc dich den Merchant
    purpose = models.IntegerField(choices=SaleReportFormPurposeTypes.CHOICES, default=0, null=False, blank=False)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sale_report_created"
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sale_report_updated"
    )

    # Noi dung mo moi
    new_merchant_name = models.CharField(max_length=255, help_text='Noi dung mo moi merchant_name', null=True)
    new_merchant_brand = models.CharField(max_length=255, help_text='Noi dung mo moi merchant_brand', null=True)
    new_address = models.TextField(help_text='Noi dung mo moi address', null=True)
    new_customer_name = models.CharField(max_length=255, help_text='Noi dung mo moi customer_name', null=True)
    new_phone = models.CharField(max_length=100, help_text='Noi dung mo moi phone', null=True)
    new_result = models.IntegerField(choices=SaleReportFormCreateNewResults.CHOICES, null=True, blank=True,
                                     help_text='Noi dung mo moi result')
    new_using_application = models.CharField(choices=SaleReportFormNewUsingApplications.CHOICES, max_length=100,
                                             null=True, blank=True)
    new_note = models.TextField(help_text='Noi dung ghi chu', null=True)

    # Noi dung Cham soc, Trien Khai
    shop_code = models.CharField(max_length=100, help_text='Relative with shop.code', null=True, blank=True)
    shop_status = models.IntegerField(choices=SaleReportFormShopStatus.CHOICES, default=0, null=True, blank=True)
    image_outside = models.ImageField(
        upload_to='sale_report_form',
        help_text='Noi dung Cham soc - KQ cham soc, Noi dung Trien khai - image_outside',
        blank=True
    )
    image_inside = models.ImageField(
        upload_to='sale_report_form',
        help_text='Noi dung Cham soc - KQ cham soc, Noi dung Trien khai - image_outside',
        blank=True
    )
    image_store_cashier = models.ImageField(
        upload_to='sale_report_form',
        help_text='Noi dung Cham soc - KQ cham soc, Noi dung Trien khai - image_store_cashier',
        blank=True
    )

    # Noi dung Cham soc - Cua hang nghi kinh doanh
    cessation_of_business_note = models.TextField(
        help_text='Noi dung Cham soc - Cua hang nghi kinh doanh - note',
        null=True
    )
    cessation_of_business_image = models.ImageField(
        upload_to='sale_report_form',
        help_text='Noi dung Cham soc - Cua hang nghi kinh doanh - image',
        blank=True
    )

    # Noi dung Cham soc - Ket qua cham soc
    customer_care_posm = models.TextField(help_text='Noi dung Cham soc - KQ cham soc - POSM', null=True)
    customer_care_cashier_reward = models.IntegerField(
        choices=SaleReportFormCashierReward.CHOICES,
        default=0,
        null=True,
        blank=True,
        help_text='Noi dung Cham soc - KQ cham soc - cashier_reward'
    )
    customer_care_transaction = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        help_text='Noi dung Cham soc - KQ cham soc - care_transaction'
    )

    # Noi dung Trien khai
    implement_posm = models.TextField(help_text='Noi dung Trien khai - POSM', null=True)
    implement_merchant_view = models.TextField(help_text='Noi dung Trien khai - merchant_view', null=True)
    implement_career_guideline = models.TextField(help_text='Noi dung Trien khai - career_guideline', null=True)
    implement_confirm = models.IntegerField(choices=SaleReportFormShopConfirm.CHOICES, null=True, blank=True,
                                            help_text='Noi dung xac nhan cua hang')
    implement_new_address = models.TextField(help_text='Noi dung chuyen den dia chi moi', null=True)

    # Bản nháp hay bản chính thức
    is_draft = models.BooleanField(default=True)

    class Meta:
        db_table = 'sale_report_form'
        ordering = ['-created_date']
        default_permissions = ()

    def get_shop(self):
        try:
            shop = Shop.objects.filter(code=self.shop_code).first()
        except Shop.DoesNotExist:
            shop = None
        return shop

    def get_team(self):
        teams = []
        if self.created_by is not None:
            try:
                staff = Staff.objects.filter(email=self.created_by.email).order_by('-staff').first()
                if staff is not None:
                    for team in staff.team.all():
                        teams.append(team.code)
                    return teams
                return None
            except Staff.DoesNotExist:
                return None
