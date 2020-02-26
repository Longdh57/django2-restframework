from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from sale_portal.user.models import User
from sale_portal.administrative_unit.models import QrProvince


class Area(models.Model):
    name = models.CharField(max_length=100, null=False)
    code = models.CharField(max_length=10, null=False)
    provinces = models.TextField()
    proportion_kpi_s73 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    user = models.ManyToManyField(User)

    class Meta:
        db_table = 'area'
        ordering = ['code']
        default_permissions = ()
        permissions = (
            ('area_list_data', 'Can get area list data'),
            ('area_detail', 'Can get area detail'),
            ('area_create', 'Can create area'),
            ('area_edit', 'Can edit area'),
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if isinstance(self.provinces, list):
            self.provinces = ','.join(self.provinces)
        super(Area, self).save(*args, **kwargs)

    def get_provinces(self):
        province_ids = self.provinces.split(',')
        return QrProvince.objects.filter(province_code__in=province_ids)
