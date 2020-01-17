from django.db import models
from sale_portal.administrative_unit.models import QrProvince


class Area(models.Model):
    name = models.CharField(max_length=100, null=False)
    code = models.CharField(max_length=10, null=False)
    provinces = models.TextField()

    class Meta:
        db_table = 'area'
        ordering = ['code']
        default_permissions = ()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if isinstance(self.provinces, list):
            self.provinces = ','.join(self.provinces)
        super(Area, self).save(*args, **kwargs)

    def get_provinces(self):
        province_ids = self.provinces.split(',')
        return QrProvince.objects.filter(province_code__in=province_ids)
