from django.contrib import admin
from django.contrib.admin import ModelAdmin

from accounts.models import Profile


class ProfileAdmin(ModelAdmin):
    list_display = ['full_name', 'role', 'user']
    list_display_links = ['full_name']
    list_filter = ['role']
    list_per_page = 18
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'role']


# Register your models here.
admin.site.register(Profile, ProfileAdmin)