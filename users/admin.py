from django.contrib import admin
from .models import User


@admin.register(User)
class SimpleUserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_staff", "is_active", "date_joined")
    search_fields = ("email",)
    readonly_fields = ("date_joined", "last_login")
    fields = ("email", "first_name", "last_name", "is_active", "is_staff", "is_superuser", "groups", "user_permissions", "password", "last_login", "date_joined")
