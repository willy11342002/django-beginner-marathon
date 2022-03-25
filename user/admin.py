from django.contrib.auth.admin import GroupAdmin as origin_GroupAdmin
from django.contrib.auth.admin import UserAdmin as origin_UserAdmin
from django.contrib.auth.models import Group as origin_Group
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from . import models
from . import forms


class UserAdmin(origin_UserAdmin):
    fieldsets = [
        [None, {'fields': ['username', 'password',]}],
        [_('Personal info'), {'fields': ['name',]}],
        [_('Permissions'), {'fields': ['is_active',]}],
        [_('Important dates'), {'fields': ['last_login', 'date_joined']}],
    ]


class GroupAdmin(origin_GroupAdmin):
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_manager:
            return False
        if obj and not request.user.groups.filter(pk=obj.id).first():
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_manager:
            return False
        if obj and not request.user.groups.filter(pk=obj.id).first():
            return False
        return super().has_change_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            return form

        permissions = form.base_fields.get('permissions')
        if permissions:
            user_permissions = {p.id for p in request.user.user_permissions.all()}
            for group in request.user.groups.all():
                user_permissions |= {p.id for p in group.permissions.all()}

            permissions.queryset = permissions.queryset.filter(pk__in=user_permissions)

        return form


class StaffAdmin(origin_UserAdmin):
    form = forms.UserChangeForm
    readonly_fields = ('last_login', 'date_joined', 'username',)
    fieldsets = [
        [None, {'fields': ['username', 'password']}],
        [_('Permissions'), {'fields': ['is_active', 'is_manager', 'groups', 'user_permissions']}],
        [_('Important dates'), {'fields': ['last_login', 'date_joined']}],
    ]

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and not request.user.is_manager:
            return list(self.readonly_fields)+\
                [field.name for field in obj._meta.fields]+\
                [field.name for field in obj._meta.many_to_many]
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request

        if request.user.is_superuser:
            return form

        groups = form.base_fields.get('groups')
        if groups:
            groups_ids = [g.id for g in obj.groups.all()] + [g.id for g in request.user.groups.all()]
            groups.queryset = groups.queryset.filter(pk__in=groups_ids)

        user_permissions = form.base_fields.get('user_permissions')
        if user_permissions:
            user_permissions_ids = [g.id for g in obj.user_permissions.all()] + [g.id for g in request.user.user_permissions.all()]
            user_permissions.queryset = user_permissions.queryset.filter(pk__in=user_permissions_ids)

        return form

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        return super().save_model(request, obj, form, change)


admin.site.unregister(origin_Group)

admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.UserProxy, UserAdmin)
admin.site.register(models.StaffProxy, StaffAdmin)

admin.site.site_header = _('Administrader System')
