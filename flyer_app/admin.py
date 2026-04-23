from django.contrib import admin

from .models import BirthdayFlyer


@admin.register(BirthdayFlyer)
class BirthdayFlyerAdmin(admin.ModelAdmin):
    list_display = ('celebrant_name', 'birthday_date', 'theme', 'created_at')
    search_fields = ('celebrant_name',)
    list_filter = ('theme', 'created_at')
