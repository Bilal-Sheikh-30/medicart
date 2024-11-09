from django.contrib import admin
from .models import CustomUser, Vendor,Address

from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserSignupForm
# Register your models here.

admin.site.register(Vendor)
admin.site.register(Address)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserSignupForm
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (  # Add additional fields to the admin form
        (None, {'fields': ('user_type', 'gender')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name','last_name', 'email', 'user_type', 'gender', 'username','password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
