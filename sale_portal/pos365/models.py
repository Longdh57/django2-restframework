from django.db import models

from sale_portal.user.models import User
from sale_portal.staff.models import Staff
from sale_portal.pos365 import Pos365ContractDuration


class Pos365(models.Model):
    code = models.CharField(max_length=100, unique=True, null=False)
    name = models.CharField(max_length=100, null=False)
    contract_duration = models.IntegerField(choices=Pos365ContractDuration.CHOICES, default=0)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, related_name='pos365s', null=True)
    contract_start_date = models.DateTimeField(null=True)
    contract_file = models.FileField(upload_to='pos365s/%Y/%m/%d/', null=True)
    customer_name = models.CharField(max_length=255, null=True)
    customer_phone = models.CharField(max_length=50, null=True)
    customer_delegate_person = models.CharField(max_length=255, null=True)
    customer_address = models.CharField(max_length=255, null=True)
    point = models.IntegerField(blank=False, null=False, default=0)
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

    @property
    def team(self):
        return self.staff.team