from django.contrib import admin

from engagement.models import Like, Comment

# Register your models here.
admin.site.register(Comment)
admin.site.register(Like)