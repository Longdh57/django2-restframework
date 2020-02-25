from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, UserManager, Group

from sale_portal.staff import StaffTeamRoleType
from sale_portal.user import ROLE_ADMIN, ROLE_OTHER, ROLE_SALE_LEADER, ROLE_SALE


class CustomUserManager(UserManager):
    pass


class User(AbstractUser):
    is_area_manager = models.BooleanField(default=False)
    is_sale_admin = models.BooleanField(default=False)
    send_disable_shop_email = models.BooleanField(default=False)

    objects = CustomUserManager()

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.email

    def get_group(self):
        group = self.groups.first()
        if group is None:
            return None
        else:
            custom_group = CustomGroup.objects.filter(group_ptr=group).first()
            return custom_group

    def get_role_name(self):
        if self.is_superuser:
            return ROLE_ADMIN
        group = self.groups.first()
        if group is None:
            return ROLE_OTHER
        return group.name


class CustomGroup(Group):
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='groups_created', null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='groups_updated', null=True)

    objects = models.Manager()

    class Meta:
        db_table = "custom_group"
        default_permissions = ()
        ordering = ['name']

    def __str__(self):
        return self.name


# class CustomGroup(models.Model):
#     group = models.OneToOneField('auth.Group', unique=True, on_delete=models.SET_NULL, null=True)
# #     your fields

@receiver(post_save, sender=User)
def assign_role_to_user(sender, instance, created, **kwargs):
    if created:
        from sale_portal.staff.models import Staff
        staff = Staff.objects.filter(email=instance.email).first()
        if staff is not None and staff.status == 1:
            if staff.team and staff.role and staff.role == StaffTeamRoleType.TEAM_MANAGEMENT:
                sale_group = Group.objects.filter(name=ROLE_SALE_LEADER).first()
            else:
                sale_group = Group.objects.get(name=ROLE_SALE)

            if sale_group is None:
                raise Exception('INTERNAL_SEVER_ERROR: GROUP_NOT_FOUND')

            instance.groups.add(sale_group)
