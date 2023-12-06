from django.contrib import admin
from users.models import CustomUser, Permission, Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm

from .forms import CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin


class GroupInline(admin.TabularInline):
    model = CustomUser.groups.through


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserCreationForm
    fieldsets = (
        (None, {'fields': ('username', 'password', 'first_name', 'last_name', 'email', )}),
        (_('Important dates'), {'fields': ('last_login', )})
    )
    list_display = ('username', 'is_staff', )
    list_filter = ('is_staff', 'is_superuser', 'is_active', )
    search_fields = ('username', )
    inlines = [
        GroupInline
    ]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    fields = ('name', )
