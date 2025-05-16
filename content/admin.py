from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline

from content.models import Article, Bulletin, Subscription


class ArticleAdmin(ModelAdmin):
    list_display = ['title', 'bulletin', 'author']
    list_filter = ['status', 'bulletin']
    search_fields = ['title']
    readonly_fields = ['created', 'updated']


class BulletinAdmin(ModelAdmin):
    list_display = ['title', 'owner', 'articles_count', 'subscriber_count']
    readonly_fields = ['created', 'updated']

    def subscriber_count(self, obj):
        return obj.subscribers.count()
    subscriber_count.short_description = 'Subscribers'

    def articles_count(self, obj):
        return obj.articles.count()
    articles_count.short_description = 'Articles'


class SubscriptionAdmin(ModelAdmin):
    list_display = ['bulletin', 'subscriber']

# Register your models here.
admin.site.register(Article, ArticleAdmin)
admin.site.register(Bulletin, BulletinAdmin)
admin.site.register(Subscription, SubscriptionAdmin)