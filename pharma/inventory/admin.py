from django.contrib import admin
from .models import CustomUser, Vendor
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Vendor)
