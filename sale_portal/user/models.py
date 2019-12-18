from django.contrib.auth.models import AbstractUser, UserManager, Group
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from ..staff.models import Staff
from ..staff import StaffTeamRoleType


class CustomUserManager(UserManager):
    pass


class User(AbstractUser):
    is_area_manager = models.BooleanField(default=False)
    send_disable_shop_email = models.BooleanField(default=False)

    objects = CustomUserManager()

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.email


@receiver(post_save, sender=User)
def create_user_group_permission(sender, instance, created, **kwargs):
    if created:
        staff = Staff.objects.filter(email=instance.email).first()
        if staff is not None:
            if staff.team and staff.role:
                if staff.role.code == StaffTeamRoleType.CHOICES[StaffTeamRoleType.TEAM_MANAGEMENT][1]:
                    sale_manager_group = Group.objects.get(name='Sale Manager')
                    instance.groups.add(sale_manager_group)
                else:
                    sale_group = Group.objects.get(name='Nhân viên Sale')
                    instance.groups.add(sale_group)
