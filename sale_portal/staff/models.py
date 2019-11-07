from django.db import models
from django.contrib.postgres.fields import JSONField

from sale_portal.staff import StaffLogType


class QrStaff(models.Model):
    staff_id=models.IntegerField(primary_key=True, unique=True)
    staff_code=models.TextField(null=True)
    nick_name=models.TextField(null=True)
    full_name=models.TextField(null=True)
    email=models.TextField(null=True)
    mobile=models.TextField(null=True)
    department_code=models.TextField(null=True)
    status=models.IntegerField(default=1,null=True)
    created_date=models.DateTimeField(null=True)
    modify_date=models.DateTimeField(null=True)
    department_id=models.IntegerField(null=True)

    class Meta:
        db_table='qr_staff'
        default_permissions = ()

    def __str__(self):
        return self.email


class Staff(models.Model):
    staff_code = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.staff_code')
    nick_name = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.nick_name')
    full_name = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.full_name')
    email = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.email')
    mobile = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.mobile')
    department_code = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.department_code')
    status = models.IntegerField(default=1, help_text='Equivalent with qr_staff.status')
    department_id = models.IntegerField(null=True, help_text='Equivalent with qr_staff.department_id')
    created_date = models.DateTimeField(null=True, help_text='Equivalent with qr_staff.created_date')
    modify_date = models.DateTimeField(null=True, help_text='Equivalent with qr_staff.modify_date')

    class Meta:
        db_table = 'staff'
        default_permissions = ()

    def __str__(self):
        return self.email


class StaffLog(models.Model):
    old_data = JSONField(blank=True, default=dict)
    new_data = JSONField(blank=True, default=dict)
    type = models.IntegerField(choices=StaffLogType.CHOICES)
    staff_id = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'staff_log'
        default_permissions = ()

    def get_new_data(self):
        return self.new_data
