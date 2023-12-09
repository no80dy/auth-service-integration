from django.contrib import admin
from django.urls import path, include

import users.views

urlpatterns = [
    path('admin/logout/', users.views.logout_view, name='logout'),
    path('admin/password_change/', users.views.password_change, name='password_change'),
    path('admin/', admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
]
