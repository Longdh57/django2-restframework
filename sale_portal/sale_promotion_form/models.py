from django.db import models
import logging

from sale_portal.sale_promotion_form import PromotionStatus
from ..terminal.models import Terminal
from ..shop.models import Shop
from ..staff.models import Staff
from ..user.models import User


class SalePromotionTitle(models.Model):
    code = models.CharField(max_length=20, unique=True, null=False, blank=False)
    description = models.TextField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sale_promotion_title'
        default_permissions = ()


class SalePromotion(models.Model):

    terminal = models.ForeignKey(Terminal, on_delete=models.SET_NULL, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.ForeignKey(SalePromotionTitle, on_delete=models.SET_NULL, null=True, blank=True)

    contact_person = models.CharField(max_length=100, help_text='contact_person', null=True)
    contact_phone_number = models.CharField(max_length=20, help_text='contact_phone_number', null=True)
    contact_email = models.CharField(max_length=100, help_text='contact_email', null=True)

    tentcard_ctkm = models.BooleanField(default=False)
    wobbler_ctkm = models.BooleanField(default=False)
    status = models.IntegerField(choices=PromotionStatus.CHOICES, null=False, default=0)

    image = models.ImageField(
        upload_to='sale_promotion_form',
        help_text='Anh nghiem thu',
        blank=True
    )

    sub_image = models.ImageField(
        upload_to='sale_promotion_form',
        help_text='Anh nghiem thu (ảnh phụ)',
        blank=True
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sale_promotion_created_by', null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sale_promotion_updated_by', null=True)

    class Meta:
        db_table = 'sale_promotion_form'
        ordering = ['-id']
        default_permissions = ()
        permissions = (
            ('sale_promotion_list_data', 'Can get sale_promotion list data'),
            ('sale_promotion_detail', 'Can get sale_promotion detail'),
            ('sale_promotion_import', 'Can import sale_promotion'),
            ('sale_promotion_edit', 'Can edit sale_promotion'),
            ('sale_promotion_export', 'Can export data sale_promotion'),
        )

    def get_terminal(self):
        return {
            'terminal_id': self.terminal.terminal_id if self.terminal else '',
            'terminal_name': self.terminal.terminal_name if self.terminal else ''
        }

    def get_merchant(self):
        merchant = self.terminal.merchant if self.terminal else None
        return {
            'merchant_id': merchant.id if merchant else '',
            'merchant_code': merchant.merchant_code if merchant else '',
            'merchant_brand': merchant.merchant_brand if merchant else ''
        }

    def get_shop(self):
        shop = self.shop if self.shop else None
        return {
            'code': shop.code if shop else '',
            'name': shop.name if shop else '',
            'province': shop.province.province_name if (shop and shop.province) else '',
            'district': shop.district.district_name if (shop and shop.district) else '',
            'wards': shop.wards.wards_name if (shop and shop.wards) else '',
            'street': shop.street if (shop and shop.street) else '',
            'address': shop.address if (shop and shop.address) else ''
        }

    def get_staff(self):
        staff = self.staff if self.staff else None
        return {
            'staff_code': staff.staff_code if staff else '',
            'full_name': staff.full_name if staff else '',
            'email': staff.email if staff else '',
            'team_code': staff.team.code if (staff and staff.team) else ''
        }
    
    def get_title(self):
        return {
            'code': self.title.code if self.title else '',
            'description': self.title.description if self.title else ''
        }

    def get_status(self):
        try:
            status = PromotionStatus.CHOICES[self.status]
            return {
                'code': status[0],
                'description': status[1]
            }
        except Exception as e:
            logging.error(e)
            return {
                'code': '',
                'description': ''
            }
