import logging

from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.dispatch import receiver
from django.db.models import Q, Count, Func, Subquery
from django.db.models.signals import post_save
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
    staff_of_chain = models.ForeignKey(Staff, on_delete=models.SET_NULL, related_name='shop_chains', blank=True,
                                       null=True)
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
    document = SearchVectorField(null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    objects = ShopQuerySet.as_manager()

    class Meta:
        db_table = 'shop'
        ordering = ('-created_date',)
        default_permissions = ()

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Shop, self).__init__(*args, **kwargs)
        self.__important_fields = ['name', 'take_care_status', 'staff_id', 'staff_of_chain_id', 'merchant_id',
                                   'province_id', 'district_id', 'wards_id', 'street', 'activated']
        for field in self.__important_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def compare(self):
        old_data = {}
        new_data = {}
        log_type = ShopLogType.CREATED

        for field in self.__important_fields:
            orig = '__original_%s' % field
            old_data[field] = getattr(self, field)
            new_data[field] = getattr(self, orig)
            if field == 'staff_id' and getattr(self, orig) != getattr(self, field):
                log_type = ShopLogType.CHANGE_STAFF
            if field == 'take_care_status' and getattr(self, orig) != getattr(self, field):
                log_type = ShopLogType.CHANGE_TAKE_CARE_STATUS
            if field == 'activated' and getattr(self, orig) != getattr(self, field):
                log_type = ShopLogType.CHANGE_ACTIVATED
            if field not in ['staff_id', 'take_care_status', 'activated'] and getattr(self, orig) != getattr(self,
                                                                                                             field):
                log_type = ShopLogType.OTHER_UPDATE
        return old_data, new_data, log_type

    def save(self, *args, **kwargs):
        try:
            old_data, new_data, type = self.compare()
            if type == ShopLogType.CREATED:
                ShopLog.objects.create(new_data=new_data, shop_id=self.id, type=type)
            else:
                ShopLog.objects.create(old_data=old_data, new_data=new_data, shop_id=self.id, type=type)
        except Exception as e:
            logging.error('Save shop exception: %s', e)
        super(Shop, self).save(*args, **kwargs)


@receiver(post_save, sender=Shop)
def create_code(sender, instance, created, *args, **kwargs):
    if created:
        instance.code = instance.id
        instance.save()
        return

@receiver(post_save, sender=Shop)
def create_or_update_document(sender, instance, created, *args, **kwargs):
    Shop.objects.filter(pk=instance.id).update(
        document=SearchVector(vn_unaccent('address'), weight='C') + SearchVector('code', weight='B') + SearchVector(
            Subquery(Shop.objects.filter(pk=instance.id).values('merchant__merchant_brand')[:1]), weight='B')
    )
    return

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


class vn_unaccent(Func):
    function = 'vn_unaccent'
