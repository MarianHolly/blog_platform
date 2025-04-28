from django.contrib import admin

from content.models import Article, Bulletin, Subscription

# Register your models here.
admin.site.register(Article)
admin.site.register(Bulletin)
admin.site.register(Subscription)