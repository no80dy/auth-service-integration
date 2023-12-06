import json
import http
import requests

from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model, password_validation
from django import forms
from django.contrib.auth.forms import UserCreationForm


class CustomPasswordChangeFormMyself(forms.Form):
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        ),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        url = 'http://localhost:8000/api/v1/users/change_password'

        payload = {
            'username': self.user.username,
            'password': self.cleaned_data['old_password'],
            'repeated_old_password': self.cleaned_data['old_password'],
            'new_password': self.cleaned_data['new_password1']
        }
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            raise ValidationError(
                response.json(),
                code="password_incorrect",
            )
        return self.cleaned_data['old_password']


class CustomUserCreationForm(forms.ModelForm):
    def save(self, commit=True):
        url = 'http://localhost:8000/api/v1/users/signup'
        payload = {
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password'],
            'repeated_password': self.cleaned_data['password'],
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
            'email': self.cleaned_data['email']
        }
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.CREATED:
            raise ValidationError(
                response.json(),
                code="data_incorrect",
            )

    class Meta:
        model = get_user_model()
        fields = ('username', 'password', )
