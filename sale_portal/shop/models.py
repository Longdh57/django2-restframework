import logging

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db.models import Q, Count, Func, Subquery
from django.contrib.postgres.search import SearchVectorField, SearchVector

from sale_portal.user.models import User
from sale_portal.area.models import Area
from sale_portal.staff.models import Staff
from sale_portal.staff_care import StaffCareType
from sale_portal.merchant.models import Merchant
from sale_portal.shop_cube.models import ShopCube
from sale_portal.shop import ShopTakeCareStatus, ShopActivateType, ShopLogType
from sale_portal.administrative_unit.models import QrProvince, QrDistrict, QrWards


class ShopQuerySet(models.QuerySet):
    def shop_active(self):
        return self.filter(activated=ShopActivateType.ACTIVATE)

    def shop_disable(self):
        return self.annotate(count_terminals=Count('terminals')).filter(
            Q(count_terminals=0) | Q(activated=ShopActivateType.DISABLE))


class Shop(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=100, null=True, unique=True)
    address = models.TextField(null=True)
    description = models.TextField(null=True)
    take_care_status = models.IntegerField(choices=ShopTakeCareStatus.CHOICES, default=ShopTakeCareStatus.CREATED_TODAY)
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
        indexes = [
            GinIndex(fields=['document']),
        ]
        db_table = 'shop'
        ordering = ('-created_date',)
        default_permissions = ()
        permissions = (
            ('shop_list_data', 'Can get shop list data'),
            ('shop_detail', 'Can get shop detail'),
            ('shop_create', 'Can create shop'),
            ('shop_edit', 'Can edit shop'),
            ('shop_import', 'Can import data shop'),
            ('shop_export', 'Can export data shop'),
            ('dashboard_shop_count', 'Can get shop data for dashboard'),
            ('shop_assign', 'Can create shop from terminal or assign terminal to shop'),
        )

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Shop, self).__init__(*args, **kwargs)
        self.__important_fields = ['name', 'take_care_status', 'merchant_id',
                                   'province_id', 'district_id', 'wards_id', 'street', 'address', 'activated']
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
            if field == 'take_care_status' and getattr(self, orig) != getattr(self, field):
                log_type = ShopLogType.CHANGE_TAKE_CARE_STATUS
            if field == 'activated' and getattr(self, orig) != getattr(self, field):
                log_type = ShopLogType.CHANGE_ACTIVATED
            if field not in ['take_care_status', 'activated'] and getattr(self, orig) != getattr(self, field):
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

    @property
    def shop_cube(self):
        try:
            shop_cube = ShopCube.objects.filter(shop_id=self.pk).order_by('-report_date').first()
        except ShopCube.DoesNotExist:
            shop_cube = None
        return shop_cube

    @property
    def area(self):
        try:
            area = Area.objects.filter(provinces__contains=self.province.province_code).first()
        except Area.DoesNotExist:
            area = None
        return area

    @property
    def staff(self):
        staff_care = self.staff_cares.filter(type=StaffCareType.STAFF_SHOP).first()
        if staff_care is not None:
            return staff_care.staff
        return None

    @property
    def team(self):
        staff_care = self.staff_cares.filter(type=StaffCareType.STAFF_SHOP).first()
        if staff_care is not None:
            return staff_care.staff.team
        return None

    @property
    def staff_of_chain(self):
        staff_care = self.staff_cares.filter(type=StaffCareType.STAFF_OF_CHAIN_SHOP).first()
        if staff_care is not None:
            return staff_care.staff
        return None

    @property
    def team_of_chain(self):
        staff_care = self.staff_cares.filter(type=StaffCareType.STAFF_OF_CHAIN_SHOP).first()
        if staff_care is not None:
            return staff_care.staff.team
        return None

    def staff_create(self, staff_id, request=None):
        staff_care = self.staff_cares.filter(type=StaffCareType.STAFF_SHOP).first()
        if staff_care is None:
            try:
                staff = Staff.objects.filter(pk=staff_id).first()
                if staff is None:
                    raise Exception('Staff is not exist')
                if staff.status != 1:
                    raise Exception('Staff status not activate')

                staff_care = self.staff_cares.create(
                    staff_id=staff_id,
                    merchant_id=None,
                    type=StaffCareType.STAFF_SHOP
                )
                create_staff_care_log(self, staff_id, StaffCareType.STAFF_SHOP, request)
                return staff_care.staff
            except Exception as e:
                logging.error('Create staff-shop exception: %s', e)
                raise Exception('Create staff-shop exception: %s', e)
        else:
            raise Exception('Shop already exist a staff ')

    def staff_delete(self, request=None):
        try:
            remove_staff_care(self, StaffCareType.STAFF_SHOP, request)
        except Exception as e:
            logging.error('Delete staff-shop exception: %s', e)
            raise Exception('Delete staff-shop exception: %s', e)

    def staff_of_chain_create(self, staff_id, request=None):
        staff_care = self.staff_cares.filter(type=StaffCareType.STAFF_OF_CHAIN_SHOP).first()
        if staff_care is None:
            try:
                staff_care = self.staff_cares.create(
                    staff_id=staff_id,
                    merchant_id=None,
                    type=StaffCareType.STAFF_OF_CHAIN_SHOP
                )
                create_staff_care_log(self, staff_id, StaffCareType.STAFF_OF_CHAIN_SHOP, request)
                return staff_care.staff
            except Exception as e:
                logging.error('Create staff_of_chain-shop exception: %s', e)
        else:
            raise Exception('Shop already exist a staff_of_chain ')

    def staff_of_chain_delete(self, request=None):
        try:
            remove_staff_care(self, StaffCareType.STAFF_OF_CHAIN_SHOP, request)
        except Exception as e:
            logging.error('Delete staff_of_chain-shop exception: %s', e)


def create_staff_care_log(shop, staff_id, type, request):
    shop.staff_care_logs.create(
        staff_id=staff_id,
        shop_id=shop.id,
        type=type,
        is_caring=True,
        created_by=request.user if request else None,
        updated_by=request.user if request else None
    )


def remove_staff_care(shop, type, request):
    shop_id = shop.id

    staff_care = shop.staff_cares.filter(type=type).first()

    staff = staff_care.staff

    staff_care.delete()

    if staff_care is not None:
        staff_care_log = shop.staff_care_logs.filter(staff=staff, type=type, is_caring=True).order_by('id').first()
        if staff_care_log is not None:
            staff_care_log.is_caring = False
            staff_care_log.updated_by_id = request.user.id if request else None
            staff_care_log.save()
        else:
            shop.staff_care_logs.create(
                staff_id=staff.id,
                shop_id=shop_id,
                type=type,
                is_caring=False,
                created_by=request.user if request else None,
                updated_by=request.user if request else None
            )


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
