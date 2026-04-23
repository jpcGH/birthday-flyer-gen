from django.contrib import admin

from .models import BirthdayFlyer, SiteBranding


@admin.register(BirthdayFlyer)
class BirthdayFlyerAdmin(admin.ModelAdmin):
    list_display = ('celebrant_name', 'birthday_date', 'theme', 'created_at')
    search_fields = ('celebrant_name',)
    list_filter = ('theme', 'created_at')


@admin.register(SiteBranding)
class SiteBrandingAdmin(admin.ModelAdmin):
    list_display = ('navbar_title', 'footer_owner', 'is_active', 'updated_at')
    list_filter = ('is_active', 'updated_at')
    search_fields = ('navbar_title', 'footer_owner')
