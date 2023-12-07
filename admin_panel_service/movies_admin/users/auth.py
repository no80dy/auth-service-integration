import http
import json

import jwt
import requests
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from .models import Permission, Group
from .settings import settings

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.LOG_IN_URL
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
        user.first_name = decoded_token.get('first_name')
        user.last_name = decoded_token.get('last_name')
        user.email = decoded_token.get('email')

        groups = []
        for group_permissions in decoded_token.get('groups_permissions'):
            permissions = [
                Permission.objects.get_or_create(name=permission)[0]
                for permission in group_permissions['permissions']
            ]
            group, _ = Group.objects.get_or_create(name=group_permissions['group'])
            group.permissions.set(permissions)
            group.save()

            groups.append(group)
            if group_permissions['group'] == 'superuser':
                user.is_superuser = True

        user.groups.set(groups)
        user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExists:
            return None
