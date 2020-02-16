from django.db import models


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
    number_of_tran = models.TextField(blank=True, null=True, help_text='SLGD hom qua')
    number_of_tran_w_1_7 = models.TextField(blank=True, null=True, help_text='SLGD ky 1')
    number_of_tran_w_8_14 = models.TextField(blank=True, null=True, help_text='SLGD ky 2')
    number_of_tran_w_15_21 = models.TextField(blank=True, null=True, help_text='SLGD ky 3')
    number_of_tran_w_22_end = models.TextField(blank=True, null=True, help_text='SLGD ky 4')
    point_w_1_7 = models.IntegerField(default=0, help_text='Point ky 1')
    point_w_8_14 = models.IntegerField(default=0, help_text='Point ky 2')
    point_w_15_21 = models.IntegerField(default=0, help_text='Point ky 3')
    point_w_22_end = models.IntegerField(default=0, help_text='Point ky 4')
    point_last_m_w_1_7 = models.IntegerField(default=0, help_text='Point ky 1 thang truoc')
    point_last_m_w_8_14 = models.IntegerField(default=0, help_text='Point ky 2 thang truoc')
    point_last_m_w_15_21 = models.IntegerField(default=0, help_text='Point ky 3 thang truoc')
    point_last_m_w_22_end = models.IntegerField(default=0, help_text='Point ky 4 thang truoc')
    _created_date = models.DateTimeField(blank=True, null=True)
    _updated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'shop_cube'
        default_permissions = ()

    def __str__(self):
        return str(self.shop_id)
