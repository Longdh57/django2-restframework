from django.db import models

from sale_portal.team.models import Team
from sale_portal.user.models import User
from sale_portal.staff.models import Staff
from sale_portal.pos365 import Pos365ContractDuration
from sale_portal.administrative_unit.models import QrProvince


class Pos365(models.Model):
    code = models.CharField(max_length=100, unique=True, null=False, help_text='Số hợp đồng')
    contract_duration = models.IntegerField(choices=Pos365ContractDuration.CHOICES, default=0)
    contract_coefficient = models.IntegerField(default=100, help_text='Hệ số hợp đồng, tỷ lệ từ 0 đến 100')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, related_name='pos365s', null=True)
    contract_team = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name='pos365s', null=True,
                                      help_text='Team - dùng trong TH hợp đồng của cộng tác viên')
    contract_start_date = models.DateTimeField(null=True)
    contract_url = models.TextField(null=True, help_text='Link phần mềm')
    contract_product_quantity = models.IntegerField(default=1, null=True, help_text='Số lượng sản phẩm')
    contract_product_series = models.TextField(null=True, help_text='Series thiết bị bán/cho thuê')
    contract_revenue = models.IntegerField(default=0, null=True, help_text='Doanh thu')
    contract_note = models.TextField(null=True, help_text='Ghi chú')
    contract_file = models.FileField(upload_to='pos365s/%Y/%m/%d/', null=True)
    customer_merchant = models.CharField(max_length=255, null=True)
    customer_name = models.CharField(max_length=255, null=True)
    customer_phone = models.CharField(max_length=50, null=True)
    customer_address = models.CharField(max_length=255, null=True)
    customer_province = models.ForeignKey(QrProvince, on_delete=models.SET_NULL, related_name='pos365s', blank=True,
                                          null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='pos365_created_by', null=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='pos365_updated_by', null=True)

    class Meta:
        db_table = 'pos365'
        ordering = ['-created_date']
        default_permissions = ()
        permissions = (
            ('pos365_list_data', 'Can get pos365 list data'),
            ('pos365_create', 'Can create pos365'),
            ('pos365_detail', 'Can get pos365 detail'),
            ('pos365_edit', 'Can edit pos365'),
            ('pos365_export', 'Can export data pos365'),
            ('pos365_extend_the_duration', 'Có thể gia hạn HĐ'),
        )

    @property
    def team(self):
        if self.contract_team is not None:
            return self.contract_team
        return self.staff.team

    @property
    def area(self):
        if self.contract_team is not None:
            team = self.contract_team
        else:
            team = self.staff.team
        if team:
            return team.area
        return
