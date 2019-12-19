import logging

from django.db import models
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import JSONField

from sale_portal.team.models import Team
from sale_portal.staff import StaffLogType
from ..user.models import User


class StaffTeamRole(models.Model):
    code = models.CharField(max_length=50, unique=True)
    group = models.OneToOneField(Group, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'staff_team_role'
        default_permissions = ()

    def __str__(self):
        return self.code


class QrStaff(models.Model):
    staff_id = models.IntegerField(primary_key=True, unique=True)
    staff_code = models.TextField(null=True)
    nick_name = models.TextField(null=True)
    full_name = models.TextField(null=True)
    email = models.TextField(null=True)
    mobile = models.TextField(null=True)
    department_code = models.TextField(null=True)
    status = models.IntegerField(default=1, null=True)
    created_date = models.DateTimeField(null=True)
    modify_date = models.DateTimeField(null=True)
    department_id = models.IntegerField(null=True)

    class Meta:
        db_table = 'qr_staff'
        default_permissions = ()

    def __str__(self):
        return self.email


class Staff(models.Model):
    staff_code = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.staff_code')
    nick_name = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.nick_name')
    full_name = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.full_name')
    email = models.CharField(max_length=200, null=True, unique=True, help_text='Equivalent with qr_staff.email')
    mobile = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.mobile')
    department_code = models.CharField(max_length=200, null=True, help_text='Equivalent with qr_staff.department_code')
    status = models.IntegerField(default=1, help_text='Equivalent with qr_staff.status')
    department_id = models.IntegerField(null=True, help_text='Equivalent with qr_staff.department_id')
    created_date = models.DateTimeField(null=True, help_text='Equivalent with qr_staff.created_date')
    modify_date = models.DateTimeField(null=True, help_text='Equivalent with qr_staff.modify_date')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(StaffTeamRole, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'staff'
        ordering = ['-created_date']
        default_permissions = ()
        permissions = (
            ('staff_list_data', 'Can get staff list data'),
            ('staff_detail', 'Can get staff detail'),
            ('staff_edit', 'Can edit staff'),
            ('staff_import', 'Can import data staff'),
        )

    def __str__(self):
        return self.email

    def __init__(self, *args, **kwargs):
        super(Staff, self).__init__(*args, **kwargs)
        self.__important_fields = ['team_id', 'role_id']
        for field in self.__important_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def compare(self):
        old_data = {}
        new_data = {}
        type = StaffLogType.CREATE_NEW

        for field in self.__important_fields:
            orig = '__original_%s' % field
            old_data[field] = getattr(self, field)
            new_data[field] = getattr(self, orig)
            if getattr(self, orig) != getattr(self, field):
                type = StaffLogType.UPDATED
        return old_data, new_data, type

    def save(self, *args, **kwargs):
        try:
            if kwargs.get('log_type') and kwargs.get('old_team_id') is None and kwargs.get('old_team_code') is None:
                StaffLog.objects.create(
                    staff_id=kwargs.get('staff_id'),
                    team_id=kwargs.get('team_id'),
                    team_code=kwargs.get('team_code'),
                    role_id=kwargs.get('role_id'),
                    type=kwargs.get('log_type'),
                    description=kwargs.get('description'),
                )

            if kwargs.get('log_type') and kwargs.get('old_team_id') and kwargs.get('old_team_code'):
                StaffLog.objects.create(
                    staff_id=kwargs.get('staff_id'),
                    team_id=kwargs.get('old_team_id'),
                    team_code=kwargs.get('old_team_code'),
                    role_id=None,
                    type=StaffLogType.OUT_TEAM,
                    description=kwargs.get('description'),
                )
                StaffLog.objects.create(
                    staff_id=kwargs.get('staff_id'),
                    team_id=kwargs.get('team_id'),
                    team_code=kwargs.get('team_code'),
                    role_id=kwargs.get('role_id'),
                    type=StaffLogType.JOIN_TEAM,
                    description=kwargs.get('description'),
                )

            if kwargs.get('log_type') is None and type == StaffLogType.UPDATED:
                old_data, new_data, type = self.compare()
                StaffLog.objects.create(old_data=old_data, new_data=new_data, staff_id=self.id, type=type)

        except Exception as e:
            logging.error('Staff_log exception: %s', e)

        super(Staff, self).save()


class StaffLog(models.Model):
    old_data = JSONField(blank=True, default=dict)
    new_data = JSONField(blank=True, default=dict)
    type = models.IntegerField(choices=StaffLogType.CHOICES)
    staff_id = models.IntegerField(blank=True, null=True)
    team_id = models.IntegerField(blank=True, null=True)
    team_code = models.CharField(max_length=20, blank=True, null=True)
    role_id = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='staff_log_created_by', null=True)

    class Meta:
        db_table = 'staff_log'
        default_permissions = ()

    def get_new_data(self):
        return self.new_data
