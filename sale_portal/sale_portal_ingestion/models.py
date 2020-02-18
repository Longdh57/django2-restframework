from django.db import models


class MidTidShop(models.Model):
    merchant_code = models.CharField(max_length=255, null=True, blank=True)
    merchant_name = models.CharField(max_length=255, null=True, blank=True)
    terminal_id = models.CharField(max_length=255, null=True, blank=True)
    terminal_name = models.CharField(max_length=255, null=True, blank=True)
    terminal_geo_check = models.IntegerField(default=0)
    terminal_geo_generate = models.IntegerField(default=0)
    terminal_latitude = models.FloatField(null=True)
    terminal_longitude = models.FloatField(null=True)
    shop_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'sale_portal_ingestion'
        db_table = 'mid_tid_shop'
        ordering = ('shop_id',)
        default_permissions = ()

    def __str__(self):
        return self.shop_id + ' - ' + self.merchant_code + ' - ' + self.terminal_id


class ShopList(models.Model):
    shop_id = models.CharField(max_length=255, null=True, blank=True)
    shop_province_code = models.CharField(max_length=255, null=True, blank=True)
    shop_province_name = models.CharField(max_length=255, null=True, blank=True)
    shop_district_code = models.CharField(max_length=255, null=True, blank=True)
    shop_district_name = models.CharField(max_length=255, null=True, blank=True)
    shop_ward_code = models.CharField(max_length=255, null=True, blank=True)
    shop_ward_name = models.CharField(max_length=255, null=True, blank=True)
    shop_area = models.CharField(max_length=255, null=True, blank=True)
    shop_address = models.CharField(max_length=255, null=True, blank=True)
    merchant_code = models.CharField(max_length=255, null=True, blank=True)
    merchant_brand = models.CharField(max_length=255, null=True, blank=True)
    department_name = models.CharField(max_length=255, null=True, blank=True)
    sale_name = models.CharField(max_length=255, null=True, blank=True)
    sale_email = models.CharField(max_length=255, null=True, blank=True)
    merchant_group_bussiness_type = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    shop_created_date = models.DateField()
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    geo_check = models.IntegerField(default=0)
    geo_generate = models.IntegerField(default=0)

    class Meta:
        app_label = 'sale_portal_ingestion'
        db_table = 'shop_list'
        ordering = ('shop_id',)
        default_permissions = ()

    def __str__(self):
        return self.shop_id
