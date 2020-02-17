from django.db import models

from django.core.validators import MaxValueValidator, MinValueValidator

from sale_portal.area.models import Area
from sale_portal.pos365 import Pos365ContractDuration
from sale_portal.config_kpi import ProportionKpiTeamType


class ExchangePointPos365(models.Model):
    type = models.IntegerField(choices=Pos365ContractDuration.CHOICES, unique=True)
    point = models.IntegerField(default=0)

    class Meta:
        db_table = 'exchange_point_pos365'
        default_permissions = ()
        permissions = (
            ('list_exchange_point_pos365_config', 'Can get exchange point pos365 config list '),
        )

    def __str__(self):
        return Pos365ContractDuration.CHOICES[self.type][1]


class ProportionKpiTeam(models.Model):
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, related_name='proportion_kpi', null=True, blank=True)
    type = models.IntegerField(choices=ProportionKpiTeamType.CHOICES)
    leader_coefficient = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        db_table = 'proportion_kpi_team'
        default_permissions = ()
        unique_together = ('area', 'type')

    def __str__(self):
        return f'{self.area.code} - {ProportionKpiTeamType.CHOICES[self.type][1]}'
