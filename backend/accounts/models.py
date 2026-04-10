from django.contrib.auth.models import User
from django.db.models import CASCADE, Model, OneToOneField, ImageField, ForeignKey
from django.db.models.fields import CharField, TextField, DateTimeField, BooleanField
import sys

# Only import Cloudinary if not running tests
if 'test' not in sys.argv:
    from cloudinary_storage.storage import MediaCloudinaryStorage
else:
    MediaCloudinaryStorage = None


# Extending existing User model
class Profile(Model):
    USER_ROLES = [
        ('reader', 'Reader'),
        ('writer', 'Writer'),
        ('admin', 'Administrator'),
    ]

    user = OneToOneField(User, on_delete=CASCADE, related_name='profile')
    role = CharField(max_length=20, choices=USER_ROLES, default='reader')
    biography = TextField(max_length=500, null=True, blank=True)
    avatar = ImageField(
        default='default_avatar.png',
        upload_to='profile_pics/',
        storage=MediaCloudinaryStorage() if MediaCloudinaryStorage else None
    )
    auto_subscribed_to_platform = BooleanField(default=False)

    class Meta:
        ordering = ['user__username']

    def __repr__(self):
        return f"Profile(name={self.user}, role={self.role})"

    def __str__(self):
        return f"{self.user.username}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def avatar_url(self):
        """Return avatar URL with fallback to default avatar image or placeholder if not found."""
        if self.avatar and str(self.avatar) != 'default_avatar.png':
            try:
                # Return custom avatar if it exists
                return self.avatar.url
            except Exception:
                pass

        # Fall back to placeholder avatar with username initials
        initials = self.user.username[:2].upper()
        return f'https://ui-avatars.com/api/?name={self.user.username}&background=1e40af&color=fff&size=128'

    @property
    def is_reader(self):
        return self.role == 'reader'

    @property
    def is_writer(self):
        return self.role == 'writer'

    @property
    def is_admin(self):
        return self.role == 'admin'

    def get_articles_count(self):
        """Get count of articles written by this user (if writer)."""
        if self.is_writer and hasattr(self, 'bulletin'):
            return self.bulletin.articles.count()
        return 0

    def get_likes_received_count(self):
        """Get count of likes received on this user's articles."""
        from content.models import Article
        from engagement.models import Like
        if self.is_writer and hasattr(self, 'bulletin'):
            articles = Article.objects.filter(bulletin=self.bulletin)
            return Like.objects.filter(article__in=articles).count()
        return 0

    def get_comments_received_count(self):
        """Get count of comments received on this user's articles."""
        from content.models import Article
        from engagement.models import Comment
        if self.is_writer and hasattr(self, 'bulletin'):
            articles = Article.objects.filter(bulletin=self.bulletin)
            return Comment.objects.filter(article__in=articles).count()
        return 0

    def get_articles_liked_count(self):
        """Get count of articles liked by this user (if reader)."""
        from engagement.models import Like
        return Like.objects.filter(user=self.user).count()

    def get_comments_posted_count(self):
        """Get count of comments posted by this user (if reader)."""
        from engagement.models import Comment
        return Comment.objects.filter(author=self.user).count()

    def get_subscriptions_count(self):
        """Get count of bulletins this user is subscribed to."""
        from content.models import Subscription
        return Subscription.objects.filter(subscriber=self).count()

    def get_bulletin_info(self):
        """Get bulletin information if user is a writer."""
        if self.is_writer and hasattr(self, 'bulletin'):
            return {
                'title': self.bulletin.title,
                'articles': self.bulletin.articles.count(),
                'subscribers': self.bulletin.subscribers.count(),
            }
        return None