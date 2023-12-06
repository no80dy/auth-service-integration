import requests
import http
import json

from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from .models import CustomUser
from .forms import CustomPasswordChangeFormMyself


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


def password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeFormMyself(CustomUser.objects.get(pk=request.user.id), request.POST)
        if form.is_valid():
            form.save()
            logout(request)
            return redirect('admin:login')
    else:
        form = CustomPasswordChangeFormMyself(CustomUser.objects.get(pk=request.user.id))
    return render(request, 'registration/password_change_form.html', {'form': form})
