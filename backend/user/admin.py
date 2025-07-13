from django.contrib import admin
from .models import UserAccount

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'role', 'permission', 'time')
    search_fields = ('email', 'role')
    list_filter = ('role', 'permission')
