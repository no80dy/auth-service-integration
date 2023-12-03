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
                    'groups',
                    'user_permissions',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login', )})
    )
    list_display = ('username', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', )
    search_fields = ('username', )
    filter_horizontal = (
        'groups',
        'user_permissions'
    )
