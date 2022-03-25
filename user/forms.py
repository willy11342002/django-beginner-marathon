from django.contrib.auth.forms import UserCreationForm as origin_UserCreationForm
from django.contrib.auth import get_user_model


class UserCreationForm(origin_UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username',)
