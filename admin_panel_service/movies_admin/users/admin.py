from django.contrib import admin
from users.models import CustomUser
from django.utils.translation import gettext_lazy as _


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login', )})
    )
    list_display = ('username', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', )
    search_fields = ('username', )
    filter_horizontal = (
        'permissions',
    )
