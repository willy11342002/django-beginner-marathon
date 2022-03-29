from django.contrib.auth.admin import GroupAdmin as origin_GroupAdmin
from django.contrib.auth.admin import UserAdmin as origin_UserAdmin
from django.contrib.auth.models import Group as origin_Group
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html_join
from admin_plus.admin import ModelAdmin
from django.contrib import admin
from itertools import groupby
from . import models
from . import forms


class UserAdmin(ModelAdmin, origin_UserAdmin):
    list_display = ('username', 'name', 'email', 'is_active')
    fieldsets = [
        [None, {'fields': ['username', 'password',]}],
        [_('Personal info'), {'fields': ['name',]}],
        [_('Permissions'), {'fields': ['is_active',]}],
        [_('Important dates'), {'fields': ['last_login', 'date_joined']}],
    ]
    search_fields = (
        (_('username'), 'username'),
        (_('email'), 'email'),
        (_('name'), 'name'),
    )


class GroupAdmin(origin_GroupAdmin):
    list_display = ('name', 'get_permissions', )

    def get_permissions(self, obj):
        dic = {'view': '查看', 'add': '新增', 'change': '修改', 'delete': '刪除'}
        permissions = obj.permissions.order_by('content_type__app_label').all()
        permissions = map(lambda obj: obj.name.split(' '), permissions)
        permissions = map(lambda obj: (_(obj[2]), dic[obj[1]]), permissions)
        permissions = (
            (model, '、'.join([p[1] for p in ps]))
            for model, ps in groupby(permissions, key=lambda p: p[0])
        )
        return format_html_join('', '<div>{}：{}</div>', permissions)
    get_permissions.short_description = '群組權限'

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

        permissions = form.base_fields.get('permissions')
        if permissions:
            permissions.queryset = permissions.queryset.exclude(content_type__app_label__in=['admin', 'contenttypes', 'sessions'])
            permissions.queryset = permissions.queryset.exclude(content_type__app_label='auth', content_type__model='group')
            permissions.queryset = permissions.queryset.exclude(content_type__app_label='user', content_type__model='user')

        if request.user.is_superuser:
            return form

        if permissions:
            user_permissions = {p.id for p in request.user.user_permissions.all()}
            for group in request.user.groups.all():
                user_permissions |= {p.id for p in group.permissions.all()}

            permissions.queryset = permissions.queryset.filter(pk__in=user_permissions)

        return form


class StaffAdmin(origin_UserAdmin):
    form = forms.UserChangeForm
    readonly_fields = ('last_login', 'date_joined', 'username',)
    list_display = ('username', 'is_active', 'is_manager', 'is_superuser', )
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

        user_permissions = form.base_fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.exclude(content_type__app_label__in=['admin', 'contenttypes', 'sessions'])
            user_permissions.queryset = user_permissions.queryset.exclude(content_type__app_label='auth', content_type__model='group')
            user_permissions.queryset = user_permissions.queryset.exclude(content_type__app_label='user', content_type__model='user')

        if request.user.is_superuser:
            return form

        groups = form.base_fields.get('groups')
        if groups:
            groups_ids = [g.id for g in obj.groups.all()] + [g.id for g in request.user.groups.all()]
            groups.queryset = groups.queryset.filter(pk__in=groups_ids)

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
