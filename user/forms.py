from django.contrib.auth.forms import UserCreationForm as origin_UserCreationForm
from django.contrib.auth.admin import UserChangeForm as origin_UserChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class UserCreationForm(origin_UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username',)


class UserChangeForm(origin_UserChangeForm):
    def clean_groups(self):
        cleaned_data = self.cleaned_data['groups']
        if self.request.user.is_superuser:
            return cleaned_data

        user_data = self.request.user.groups.all()
        old_data = self.instance.groups.all()
        if set(old_data) - set(cleaned_data) - set(user_data):
            raise ValidationError('您沒有權限進行此操作')
        return cleaned_data

    def clean_user_permissions(self):
        cleaned_data = self.cleaned_data['user_permissions']
        if self.request.user.is_superuser:
            return cleaned_data

        user_data = self.request.user.user_permissions.all()
        old_data = self.instance.user_permissions.all()
        if set(old_data) - set(cleaned_data) - set(user_data):
                raise ValidationError('您沒有權限進行此操作')
        return cleaned_data
