import json
import http
import requests

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from django import forms

from .settings import settings


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
        url = settings.CHANGE_PASSWORD_URL

        payload = {
            'username': self.user.username,
            'password': self.cleaned_data['old_password'],
            'repeated_old_password': self.cleaned_data['old_password'],
            'new_password': self.cleaned_data['new_password1']
        }
        response = requests.post(url, data=json.dumps(payload), headers={'X-Request-Id': 'auth_service'})
        if response.status_code != http.HTTPStatus.OK:
            raise ValidationError(
                response.json(),
                code="password_incorrect",
            )
        return self.cleaned_data['old_password']
