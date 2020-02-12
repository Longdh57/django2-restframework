from django.db import models

from sale_portal.user.models import User
from sale_portal.shop.models import Shop
from sale_portal.staff.models import Staff
from sale_portal.merchant.models import Merchant
from sale_portal.staff_care import StaffCareType


class StaffCare(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, related_name='staff_cares', blank=True, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, related_name='staff_cares', blank=True, null=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, related_name='staff_cares', blank=True, null=True)
    type = models.IntegerField(choices=StaffCareType.CHOICES, default=StaffCareType.STAFF_SHOP)

    class Meta:
        db_table = 'staff_care'
        default_permissions = ()
        unique_together = ('shop', 'type'), ('merchant', 'type')

    def __str__(self):
        return f'Sale email: {self.staff.email}, type care: {self.type}'


class StaffCareLog(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, related_name='staff_care_logs', blank=True, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, related_name='staff_care_logs', blank=True, null=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, related_name='staff_care_logs', blank=True,
                                 null=True)
    type = models.IntegerField(choices=StaffCareType.CHOICES, default=StaffCareType.STAFF_SHOP)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='staff_care_logs_created', null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='staff_care_logs_updated', null=True)
    is_caring = models.BooleanField(default=False)

    class Meta:
        db_table = 'staff_care_log'
        ordering = ('-created_date',)
        default_permissions = ()


class StaffCareImportLog(models.Model):
    file_url = models.FileField(
        upload_to='excel/staff-care-import-logs/',
        help_text='File imported of module staff-care',
        blank=True
    )
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'staff_care_import_log'
        default_permissions = ()
