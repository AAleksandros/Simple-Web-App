from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """Admin panel customization for CustomUser."""

    model = CustomUser
    list_display = ("email", "is_active", "is_staff", "is_superuser")
    search_fields = ("email",)
    ordering = ("email",)
    list_filter = ("is_active", "is_staff", "is_superuser")

    fieldsets = (
        ("User Information", {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        ("Create User", {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_active", "is_staff", "is_superuser"),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)