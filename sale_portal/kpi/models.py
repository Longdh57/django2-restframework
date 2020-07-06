from django.db import models


class Kpi(models.Model):
    email = models.CharField(max_length=200, null=True, unique=True, help_text='Sale email')
    kpi_target = models.IntegerField(default=0, help_text='Target KPI của sale trong mỗi tháng')
    kpi_total_point = models.IntegerField(default=0, help_text='Số lượng point hiện tại của mỗi sale')
    kpi_point_lcc = models.IntegerField(default=0, help_text='Point triển khai LCC - hệ thống đọc từ google sheet')
    kpi_point_other = models.IntegerField(default=0, help_text='Point khác - hệ thống đọc từ google sheet')

    class Meta:
        db_table = 'kpi'
        # ordering = ['-created_date']
        default_permissions = ()
        permissions = (
            ('get_data_kpi_yourself', 'Can get data kpi of yourself'),
            ('get_data_kpi_team', 'Can get data kpi of all member of team')
        )

    def __str__(self):
        return self.email