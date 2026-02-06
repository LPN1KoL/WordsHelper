from django.contrib import admin
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'first_name', 'last_name', 'username', 'auth_date')
    search_fields = ('telegram_id', 'first_name', 'last_name', 'username')
    list_filter = ('auth_date',)
    readonly_fields = ('telegram_id', 'auth_date')
