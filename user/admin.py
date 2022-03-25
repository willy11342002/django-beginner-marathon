from django.contrib.auth.admin import UserAdmin as origin_UserAdmin
from django.contrib.auth.models import Group as origin_Group
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from . import models


class UserAdmin(origin_UserAdmin):
    fieldsets = [
        [None, {'fields': ['username', 'password',]}],
        [_('Personal info'), {'fields': ['name',]}],
        [_('Permissions'), {'fields': ['is_active',]}],
        [_('Important dates'), {'fields': ['last_login', 'date_joined']}],
    ]


class StaffAdmin(origin_UserAdmin):
    fieldsets = [
        [None, {'fields': ['username', 'password']}],
        [_('Permissions'), {'fields': ['is_active', 'is_manager', 'is_staff', 'groups', 'user_permissions']}],
        [_('Important dates'), {'fields': ['last_login', 'date_joined']}],
    ]

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        return super().save_model(request, obj, form, change)


admin.site.unregister(origin_Group)

admin.site.register(models.Group)
admin.site.register(models.UserProxy, UserAdmin)
admin.site.register(models.StaffProxy, StaffAdmin)

admin.site.site_header = _('Administrader System')
