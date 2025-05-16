from django.contrib import admin

from engagement.models import Like, Comment, ReadLater

# Register your models here.
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(ReadLater)