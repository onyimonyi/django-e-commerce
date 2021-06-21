from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import RegisterForm, UserAdminChangeForm

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm  # update view
    add_form = RegisterForm  # create view
    list_display = ('email', 'full_name', 'admin', 'active', 'staff',)
    list_filter = ('admin', 'active', 'staff')
    fieldsets = (
        (None, {'fields': ('full_name', 'email', 'password')}),
        # ('FULL NAME', {'fields': ('full_name',)}),
        ('permissions', {'fields': ('admin', 'active', 'staff')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.unregister(Group)
# Register your models here.
admin.site.register(User, UserAdmin)
