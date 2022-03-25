from django.contrib.auth.models import UserManager as origin_UserManager
from django.contrib.auth.models import Group as origin_Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models


class Group(origin_Group):
    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('group')


class StaffManager(origin_UserManager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_staff=True, is_superuser=False)


class UserManager(origin_UserManager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_staff=False, is_superuser=False)


class User(AbstractUser):
    name = models.CharField(_('name'), max_length=64, null=True, blank=True)
    is_manager = models.BooleanField(_('manager status'), default=False)

    class Meta:
        verbose_name = _('all user')
        verbose_name_plural = _('all user')

class StaffProxy(User):
    objects = StaffManager()
    class Meta:
        proxy = True
        verbose_name = _('staff')
        verbose_name_plural = _('staff')


class UserProxy(User):
    objects = UserManager()
    class Meta:
        proxy = True
        verbose_name = _('user')
        verbose_name_plural = _('user')
