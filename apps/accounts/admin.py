from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Shipping details", {"fields": ("phone_number", "shipping_address")}),
    )
    list_display = ("username", "email", "is_staff", "is_active")
