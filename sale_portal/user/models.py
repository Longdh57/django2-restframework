from django.contrib.auth.models import AbstractUser, UserManager, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    if not created:
        from sale_portal.staff.models import Staff
        staff = Staff.objects.filter(email=instance.email).first()
        if staff is not None:
            if str(staff.role_id) == '1':
                sale_group = Group.objects.get(name='Sale staff')
                instance.groups.add(sale_group)
            if str(staff.role_id) == '2':
                sale_group = Group.objects.get(name='Sale manager')
                instance.groups.add(sale_group)
