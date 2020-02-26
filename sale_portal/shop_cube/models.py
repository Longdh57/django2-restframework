import datetime
from django.db import models


class ShopCubeQuerySet(models.QuerySet):
    def number_of_tran_this_week(self, value):
        dt = datetime.datetime.today()
        if value < 3:
            if dt.day <= 7:
                query = self.filter(number_of_tran_w_1_7=value)
            elif dt.day > 8 and dt.day <= 14:
                query = self.filter(number_of_tran_w_8_14=value)
            elif dt.day > 15 and dt.day <= 21:
                query = self.filter(number_of_tran_w_15_21=value)
            else:
                query = self.filter(number_of_tran_w_22_end=value)
        else:
            if dt.day <= 7:
                query = self.filter(number_of_tran_w_1_7__gte=value)
            elif dt.day > 8 and dt.day <= 14:
                query = self.filter(number_of_tran_w_8_14__gte=value)
            elif dt.day > 15 and dt.day <= 21:
                query = self.filter(number_of_tran_w_15_21__gte=value)
            else:
                query = self.filter(number_of_tran_w_22_end__gte=value)
        return query


class ShopCube(models.Model):
    shop_id = models.IntegerField(null=False, default=0, help_text='Ma shop')
    merchant_code = models.TextField(blank=True, null=True)
    merchant_group_bussiness_type = models.TextField(blank=True, null=True)
    report_date = models.DateField(null=True, blank=True, help_text='Ngay bao cao')
    shop_province_name = models.TextField(blank=True, null=True, help_text='Ten tinh thanh')
    shop_district_name = models.TextField(blank=True, null=True, help_text='Ten quan huyen')
    shop_ward_name = models.TextField(blank=True, null=True, help_text='Ten phuong xa')
    department_name = models.TextField(blank=True, null=True)
    shop_address = models.TextField(blank=True, null=True, help_text='Dia chi shop')
    number_of_tran = models.IntegerField(default=0, help_text='SLGD hom qua')
    number_of_tran_w_1_7 = models.IntegerField(default=0, help_text='SLGD ky 1')
    number_of_tran_w_8_14 = models.IntegerField(default=0, help_text='SLGD ky 2')
    number_of_tran_w_15_21 = models.IntegerField(default=0, help_text='SLGD ky 3')
    number_of_tran_w_22_end = models.IntegerField(default=0, help_text='SLGD ky 4')
    point_w_1_7 = models.IntegerField(default=0, help_text='Point ky 1')
    point_w_8_14 = models.IntegerField(default=0, help_text='Point ky 2')
    point_w_15_21 = models.IntegerField(default=0, help_text='Point ky 3')
    point_w_22_end = models.IntegerField(default=0, help_text='Point ky 4')
    point_last_m_w_1_7 = models.IntegerField(default=0, help_text='Point ky 1 thang truoc')
    point_last_m_w_8_14 = models.IntegerField(default=0, help_text='Point ky 2 thang truoc')
    point_last_m_w_15_21 = models.IntegerField(default=0, help_text='Point ky 3 thang truoc')
    point_last_m_w_22_end = models.IntegerField(default=0, help_text='Point ky 4 thang truoc')
    voucher_code_list = models.TextField(blank=True, null=True, help_text='Danh sach cac ma voucher dang ap dung')
    _created_date = models.DateTimeField(blank=True, null=True)
    _updated_date = models.DateTimeField(blank=True, null=True)

    objects = ShopCubeQuerySet.as_manager()

    class Meta:
        db_table = 'shop_cube'
        default_permissions = ()

    def __str__(self):
        return str(self.shop_id)
