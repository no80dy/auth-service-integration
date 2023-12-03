import time
from django.utils import timezone
import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have an username')
        user = self.model(
            username=username,
            last_login=timezone.now()
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class AbstractCustomBaseUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('user name'), max_length=255, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=True
    )
    is_active = models.BooleanField(
        _('is_active'),
        default=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True


class CustomUser(AbstractCustomBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f'{self.username}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    # class Meta(AbstractCustomBaseUser.Meta):
    #     swappable = 'AUTH_BASE_USER'


# class MyUserManager(BaseUserManager):
#     def create_user(self, username, password=None):
#         if not username:
#             raise ValueError('Users must have an username')
#         user = self.model(username=username)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, username, password=None):
#         user = self.create_user(username, password=password)
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user
#
#
# class Permission(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4)
#     permission_name = models.CharField(_('permission_name'), max_length=255)
#
#     class Meta:
#         db_table = "public\".\"permissions"
#         verbose_name = _('permission')
#         verbose_name_plural = _('permissions')
#
#
# class User(AbstractBaseUser):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     username = models.CharField(_('user name'), max_length=255, unique=True)
#     is_superuser = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     permissions = models.ManyToManyField(Permission, through='UserPermission')
#
#     USERNAME_FIELD = 'username'
#     objects = MyUserManager()
#
#     def __str__(self):
#         return f'{self.username}'
#
#     def is_staff(self):
#         return self.is_superuser
#
#     def has_perm(self, perm, obj=None):
#         return True
#
#     def has_module_perms(self, app_label):
#         return True
#
#     class Meta:
#         verbose_name = _('user')
#         verbose_name_plural = _('users')
#
#
# class UserPermission(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = "public\".\"user_permission"
