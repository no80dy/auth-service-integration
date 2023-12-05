import http

import jwt
import requests

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse


class AccessTokenFreshnessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                jwt.decode(request.session['access_token'], 'secret', algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                refresh_token = request.session['refresh_token']
                url = 'http://localhost:8000/api/v1/users/refresh-tokens'
                response = requests.post(url, headers={'Authorization': f'Bearer {refresh_token}'})
                request.session['access_token'] = response.json()['access_token']
                request.session['refresh_token'] = response.json()['refresh_token']
        response = self.get_response(request)
        return response


class RefreshTokenFreshnessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                jwt.decode(request.session['refresh_token'], 'secret', algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                logout(request)
                return redirect('admin:login')

        response = self.get_response(request)
        return response