from django.db import models
from django.db.models import Q, Count
from django.contrib.postgres.fields import JSONField

from sale_portal.user.models import User
from sale_portal.staff.models import Staff
from sale_portal.merchant.models import Merchant
from sale_portal.shop import ShopTakeCareStatus, ShopActivateType, ShopLogType
from sale_portal.administrative_unit.models import QrProvince, QrDistrict, QrWards


class ShopQuerySet(models.QuerySet):
    def shop_list_active(self):
        return self.annotate(count_terminals=Count('terminals')).filter(~Q(count_terminals=0)).filter(
            activated=ShopActivateType.ACTIVATE)

    def shop_none_street(self):
        return self.annotate(count_terminals=Count('terminals')).filter(~Q(count_terminals=0)) \
            .filter(activated=ShopActivateType.ACTIVATE).filter(Q(street__isnull=True) | Q(street=''))


class Shop(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=100, null=True, unique=True)
    address = models.TextField(null=True)
    description = models.TextField(null=True)
    take_care_status = models.IntegerField(choices=ShopTakeCareStatus.CHOICES, default=ShopTakeCareStatus.CREATED_TODAY)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, related_name='shops', blank=True, null=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, related_name='shops', blank=True, null=True)
    province = models.ForeignKey(QrProvince, on_delete=models.SET_NULL, related_name='shops', blank=True, null=True)
    district = models.ForeignKey(QrDistrict, on_delete=models.SET_NULL, related_name='shops', blank=True, null=True)
    wards = models.ForeignKey(QrWards, on_delete=models.SET_NULL, related_name='shops', blank=True, null=True)
    street = models.CharField(max_length=200, null=True)
    activated = models.IntegerField(choices=ShopActivateType.CHOICES, default=ShopActivateType.ACTIVATE)
    inactivated_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='shops_created', null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='shops_updated', null=True)

    objects = ShopQuerySet.as_manager()

    class Meta:
        db_table = 'shop'
        ordering = ('-created_date',)
        default_permissions = ()

    def __str__(self):
        return self.name


class ShopLog(models.Model):
    old_data = JSONField(blank=True, default=dict)
    new_data = JSONField(blank=True, default=dict)
    type = models.IntegerField(choices=ShopLogType.CHOICES)
    shop_id = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='shop_log_created', null=True)

    class Meta:
        db_table = 'shop_log'
        default_permissions = ()

    def get_new_data(self):
        return self.new_data
