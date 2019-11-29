from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    pass


class User(AbstractUser):
    is_area_manager = models.BooleanField(default=False)
    send_disable_shop_email = models.BooleanField(default=False)

    objects = CustomUserManager()

    class Meta:
        db_table='auth_user'

    def __str__(self):
        return self.email
