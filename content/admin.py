from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline

from content.models import Article, Bulletin, Subscription


class ArticleAdmin(ModelAdmin):
    """Admin interface for article moderation workflow.

    Permissions:
    - Admin-only access (enforced by Django admin)

    Features:
    - View all articles with evaluation and visibility status
    - Filter by evaluation status (pending/under_review/approved/rejected)
    - Filter by visibility (public/private)
    - Filter by publication status (draft/published)
    - Bulk actions: Mark Under Review, Approve, Reject
    - Direct editing of evaluation and visibility fields
    - Sort by creation date, author, evaluation status

    Performance:
    - select_related for bulletin and bulletin.owner (fewer queries)
    - prefetch_related for engagement counts
    """
    list_display = ['title', 'author', 'evaluation', 'visibility', 'status', 'created']
    list_filter = ['evaluation', 'visibility', 'status', 'created']
    search_fields = ['title', 'bulletin__owner__user__username']
    readonly_fields = ['created', 'updated', 'bulletin']
    list_editable = ['evaluation', 'visibility']
    date_hierarchy = 'created'
    list_per_page = 50
    actions = ['action_mark_under_review', 'action_approve', 'action_reject']

    def get_queryset(self, request):
        """Optimize queries with select_related for author and bulletin."""
        qs = super().get_queryset(request)
        return qs.select_related('bulletin', 'bulletin__owner')

    def author(self, obj):
        """Display article author (writer's name)."""
        return obj.bulletin.owner.user.get_full_name() or obj.bulletin.owner.user.username
    author.short_description = 'Author'
    author.admin_order_field = 'bulletin__owner__user__username'

    def action_mark_under_review(self, request, queryset):
        """Bulk action: Mark selected articles as under review."""
        updated = queryset.update(evaluation='under_review')
        self.message_user(request, f'{updated} article(s) marked as under review.')
    action_mark_under_review.short_description = 'Mark selected articles as under review'

    def action_approve(self, request, queryset):
        """Bulk action: Approve selected articles."""
        updated = queryset.update(evaluation='approved')
        self.message_user(request, f'{updated} article(s) approved.')
    action_approve.short_description = 'Approve selected articles'

    def action_reject(self, request, queryset):
        """Bulk action: Reject selected articles."""
        updated = queryset.update(evaluation='rejected')
        self.message_user(request, f'{updated} article(s) rejected.')
    action_reject.short_description = 'Reject selected articles'


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