from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = ("id", "username", "email", "date_created", "last_login", "is_admin", "is_staff")
    list_display_links = ("id", "username", "email")
    list_filter = ("is_admin", "is_staff", "is_superuser", "is_active", "hide_email")
    readonly_fields = ("id", "date_created", "last_login")
    search_fields = ("id", "username", "email")

    filter_horizontal = ()
    fieldsets = ()