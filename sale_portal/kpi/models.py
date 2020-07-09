from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Kpi(models.Model):
    email = models.CharField(max_length=200, null=True, help_text='Sale email')
    kpi_target = models.IntegerField(default=0, help_text='Target KPI của sale - hệ thống đọc từ google sheet')
    kpi_point_lcc = models.IntegerField(default=0, help_text='Point triển khai LCC - hệ thống đọc từ google sheet')
    kpi_point_other = models.IntegerField(default=0, help_text='Point khác - hệ thống đọc từ google sheet')
    month = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12)
        ],
        help_text='Tháng KPI có hiệu lực'
    )
    year = models.IntegerField(
        default=2020,
        validators=[
            MinValueValidator(1970),
            MaxValueValidator(3000)
        ],
        help_text='Năm KPI có hiệu lực'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kpi'
        ordering = ['-created_date']
        unique_together = ('email', 'month', 'year')
        default_permissions = ()
        permissions = (
            ('get_data_kpi_yourself', 'Can get data kpi of yourself'),
            ('get_data_kpi_team', 'Can get data kpi of all member of team')
        )

    def __str__(self):
        return self.email
