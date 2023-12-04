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

    class Meta(AbstractCustomBaseUser.Meta):
        swappable = 'AUTH_BASE_USER'
