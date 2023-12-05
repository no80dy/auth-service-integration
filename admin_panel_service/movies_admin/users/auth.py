import http
import json

import jwt
import requests
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from .models import Permission

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = 'http://localhost:8000/api/v1/users/signin'
        payload = {'username': username, 'password': password}
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None
        data = response.json()

        request.session['access_token'] = data['access_token']
        request.session['refresh_token'] = data['refresh_token']

        decoded_token = jwt.decode(
            jwt=data['access_token'],
            key='secret',
            algorithms=['HS256']
        )
        user, created = User.objects.get_or_create(id=decoded_token['user_id'])
        user.username = decoded_token.get('sub')
        user.is_superuser = '*.*' in decoded_token.get('permissions')
        permissions = [
            Permission.objects.get_or_create(name=permission_name)[0]
            for permission_name in decoded_token.get('permissions')
        ]
        user.permissions.add(*permissions)
        user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExists:
            return None
