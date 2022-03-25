from django.contrib.auth.models import Group as origin_Group
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from . import models


admin.site.unregister(origin_Group)
admin.site.register(models.User)
admin.site.register(models.Group)

admin.site.site_header = _('Administrader System')
