from django.contrib import admin
from django.contrib.admin import ModelAdmin

from accounts.models import Profile


class ProfileAdmin(ModelAdmin):
    list_display = ['role', 'user']
    list_display_links = ['role']
    list_per_page = 18


# Register your models here.
admin.site.register(Profile, ProfileAdmin)