from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import F

from accounts.models import Profile
from content.models import Bulletin


class ProfileAdmin(ModelAdmin):
    """
    Admin interface for Profile model with comprehensive user management.

    Features:
    - Display all users with role information
    - Filter by role (reader, writer, admin) and activity status (active, inactive)
    - Search by username and email
    - Display engagement metrics (articles, likes, comments, subscriptions)
    - Show bulletin information for writers
    - Edit role and is_active status
    - Display last login date and creation date

    Permissions:
    - Admin-only access (checked in has_permission)
    """

    list_display = [
        'username_display',
        'email_display',
        'role',
        'is_active_display',
        'articles_count',
        'engagement_summary',
        'last_login_display',
        'created_display'
    ]

    list_filter = ['role', 'user__is_active', 'user__date_joined']

    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']

    readonly_fields = [
        'user',
        'created_date',
        'last_login_date',
        'articles_count_readonly',
        'likes_received_readonly',
        'comments_received_readonly',
        'articles_liked_readonly',
        'comments_posted_readonly',
        'subscriptions_readonly',
        'bulletin_info_readonly'
    ]

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'created_date', 'last_login_date')
        }),
        ('Role & Status', {
            'fields': ('role',)
        }),
        ('Writer Metrics', {
            'fields': ('articles_count_readonly', 'likes_received_readonly', 'comments_received_readonly', 'bulletin_info_readonly'),
            'classes': ('collapse',)
        }),
        ('Reader Metrics', {
            'fields': ('articles_liked_readonly', 'comments_posted_readonly', 'subscriptions_readonly'),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 25

    def has_permission(self, request, view_type=None):
        """Restrict admin access to admin users only."""
        return request.user.is_staff and request.user.is_superuser

    def username_display(self, obj):
        """Display user's username."""
        return obj.user.username
    username_display.short_description = 'Username'
    username_display.admin_order_field = 'user__username'

    def email_display(self, obj):
        """Display user's email."""
        return obj.user.email
    email_display.short_description = 'Email'
    email_display.admin_order_field = 'user__email'

    def is_active_display(self, obj):
        """Display active status with visual indicator."""
        status = 'Active' if obj.user.is_active else 'Inactive'
        icon = '✓' if obj.user.is_active else '✗'
        return f'{icon} {status}'
    is_active_display.short_description = 'Status'
    is_active_display.admin_order_field = 'user__is_active'

    def articles_count(self, obj):
        """Display article count for writers."""
        if obj.is_writer:
            return obj.get_articles_count()
        return '—'
    articles_count.short_description = 'Articles'

    def engagement_summary(self, obj):
        """Display engagement summary based on role."""
        if obj.is_writer:
            likes = obj.get_likes_received_count()
            comments = obj.get_comments_received_count()
            return f'L:{likes} C:{comments}'
        elif obj.is_reader:
            likes = obj.get_articles_liked_count()
            comments = obj.get_comments_posted_count()
            return f'L:{likes} C:{comments}'
        return '—'
    engagement_summary.short_description = 'Engagement'

    def last_login_display(self, obj):
        """Display last login date."""
        if obj.user.last_login:
            return obj.user.last_login.strftime('%Y-%m-%d %H:%M')
        return 'Never'
    last_login_display.short_description = 'Last Login'
    last_login_display.admin_order_field = 'user__last_login'

    def created_display(self, obj):
        """Display account creation date."""
        return obj.user.date_joined.strftime('%Y-%m-%d')
    created_display.short_description = 'Created'
    created_display.admin_order_field = 'user__date_joined'

    # Readonly field display methods
    def created_date(self, obj):
        """Display full creation date/time in detail view."""
        return obj.user.date_joined
    created_date.short_description = 'Account Created'

    def last_login_date(self, obj):
        """Display full last login date/time in detail view."""
        if obj.user.last_login:
            return obj.user.last_login
        return 'Never logged in'
    last_login_date.short_description = 'Last Login'

    def articles_count_readonly(self, obj):
        """Display article count in detail view."""
        return obj.get_articles_count() if obj.is_writer else '—'
    articles_count_readonly.short_description = 'Articles Written'

    def likes_received_readonly(self, obj):
        """Display likes received in detail view."""
        return obj.get_likes_received_count() if obj.is_writer else '—'
    likes_received_readonly.short_description = 'Likes Received'

    def comments_received_readonly(self, obj):
        """Display comments received in detail view."""
        return obj.get_comments_received_count() if obj.is_writer else '—'
    comments_received_readonly.short_description = 'Comments Received'

    def articles_liked_readonly(self, obj):
        """Display articles liked in detail view."""
        return obj.get_articles_liked_count()
    articles_liked_readonly.short_description = 'Articles Liked'

    def comments_posted_readonly(self, obj):
        """Display comments posted in detail view."""
        return obj.get_comments_posted_count()
    comments_posted_readonly.short_description = 'Comments Posted'

    def subscriptions_readonly(self, obj):
        """Display subscriptions count in detail view."""
        return obj.get_subscriptions_count()
    subscriptions_readonly.short_description = 'Bulletins Subscribed'

    def bulletin_info_readonly(self, obj):
        """Display bulletin information for writers."""
        if obj.is_writer:
            info = obj.get_bulletin_info()
            if info:
                return f"{info['title']} ({info['articles']} articles, {info['subscribers']} subscribers)"
        return '—'
    bulletin_info_readonly.short_description = 'Bulletin Info'


# Register your models here.
admin.site.register(Profile, ProfileAdmin)