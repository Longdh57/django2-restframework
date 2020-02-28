from django.db import models


class QrProvince(models.Model):
    province_code = models.CharField(max_length=20, null=True)
    province_name = models.CharField(max_length=100, null=True)
    created_date = models.DateTimeField(null=True)
    brand_name = models.CharField(max_length=15, null=True)

    class Meta:
        db_table = 'qr_province'
        ordering = ['province_code']
        default_permissions = ()

    def __str__(self):
        return self.province_code


class QrDistrict(models.Model):
    province_code = models.CharField(max_length=20, null=True)
    district_code = models.CharField(max_length=20, null=True)
    district_name = models.CharField(max_length=200, null=True)
    created_date = models.DateTimeField(null=True)

    class Meta:
        db_table = 'qr_district'
        ordering = ('province_code', 'district_code',)
        default_permissions = ()

    def __str__(self):
        return self.district_code

    def get_province(self):
        province = QrProvince.objects.filter(province_code=self.province_code).first()
        if QrProvince.DoesNotExist:
            province = None
        return province


class QrWards(models.Model):
    province_code = models.CharField(max_length=20, null=True)
    district_code = models.CharField(max_length=20, null=True)
    wards_code = models.CharField(max_length=200, null=True)
    wards_name = models.CharField(max_length=200, null=True)
    created_date = models.DateTimeField(null=True)

    class Meta:
        db_table = 'qr_wards'
        ordering = ('province_code', 'district_code', 'wards_code',)
        default_permissions = ()

    def __str__(self):
        return self.wards_code

    def get_province(self):
        province = QrProvince.objects.filter(province_code=self.province_code).first()
        if province is None:
            province = None
        return province

    def get_district(self):
        district = QrDistrict.objects.filter(district_code=self.district_code).first()
        if district is None:
            district = None
        return district
