from django.contrib import admin
from django.contrib.admin import ModelAdmin

from engagement.models import Like, Comment, ReadLater


class CommentAdmin(ModelAdmin):
    list_display = ['author', 'article']


class LikeAdmin(ModelAdmin):
    list_display = ['author', 'article']


class ReadLaterAdmin(ModelAdmin):
    list_display = ['author', 'article']


# Register your models here.
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(ReadLater, ReadLaterAdmin)