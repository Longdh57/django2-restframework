from django.db import models

# Create your models here.
from django.contrib.postgres.fields import JSONField


class GeoData(models.Model):
    type = models.CharField(max_length=50, db_column='type', db_index=True)
    code = models.CharField(max_length=50, unique=True, primary_key=True, db_column='code')
    province_code = models.CharField(max_length=50, db_column='province_code', null=True, blank=True)
    district_code = models.CharField(max_length=150, db_column='district_code', null=True, blank=True)
    geojson = JSONField(db_column='geojson')

    class Meta:
        db_table = 'geodata'
        default_permissions = ()
        permissions = (
            ('map_geojson', 'Can get map background'),
        )

    def __str__(self):
        return self.code