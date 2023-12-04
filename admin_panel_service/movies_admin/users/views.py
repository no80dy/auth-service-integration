import requests
import http
import json

from django.shortcuts import redirect
from django.contrib.auth import logout, user_logged_out
from django.http import HttpResponse


def logout_view(request):
    url = 'http://localhost:8000/api/v1/users/logout'
    access_token = request.session.get('access_token', None)
    if not access_token:
        return HttpResponse('Unauthorized')

    response = requests.post(url, headers={'Authorization': f'Bearer {access_token}'})
    if response.status_code != http.HTTPStatus.OK:
        return HttpResponse(status=response.status_code, content=response.json()['detail'])
    logout(request)
    return redirect('admin:login')
