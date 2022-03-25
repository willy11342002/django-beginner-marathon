from django.contrib.auth.models import Group as origin_Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models


class Group(origin_Group):
    pass


class User(AbstractUser):
    name = models.CharField(_('name'), max_length=64, null=True, blank=True)
    is_manager = models.BooleanField(_('manager status'), default=False)
