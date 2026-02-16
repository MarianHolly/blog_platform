from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import Profile
from content.models import Article, Bulletin, Subscription
from engagement.models import Comment, Like, ReadLater


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django User model.
    Used in nested relationships to show basic user info.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Profile model.
    Shows user details along with profile-specific information.
    """
    user = UserSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    avatar_url = serializers.ReadOnlyField()
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'role', 'biography', 'avatar', 'avatar_url',
            'full_name', 'articles_count'
        ]
        read_only_fields = ['id', 'role']

    def get_articles_count(self, obj):
        """Count articles written by this profile (if writer)."""
        return obj.get_articles_count()


class BulletinListSerializer(serializers.ModelSerializer):
    """
    Serializer for Bulletin list view.
    Shows summary information without nested articles.
    """
    owner = ProfileSerializer(read_only=True)
    subscribers_count = serializers.SerializerMethodField()
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = Bulletin
        fields = [
            'id', 'title', 'description', 'slug', 'owner',
            'subscribers_count', 'articles_count', 'created', 'updated'
        ]
        read_only_fields = ['id', 'slug', 'created', 'updated']

    def get_subscribers_count(self, obj):
        """Count bulletin subscribers."""
        return obj.get_subscribers_count()

    def get_articles_count(self, obj):
        """Count published articles in bulletin."""
        return obj.articles.filter(status='published').count()


class BulletinDetailSerializer(BulletinListSerializer):
    """
    Serializer for Bulletin detail view.
    Extends list serializer to include recent articles.
    """
    recent_articles = serializers.SerializerMethodField()

    class Meta(BulletinListSerializer.Meta):
        fields = BulletinListSerializer.Meta.fields + ['recent_articles']

    def get_recent_articles(self, obj):
        """Get 5 most recent published articles."""
        articles = obj.articles.filter(status='published').order_by('-published')[:5]
        # Use ArticleListSerializer to avoid circular import
        return ArticleListSerializer(articles, many=True, context=self.context).data


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Serializer for Article list view.
    Shows summary without full content (for performance).
    """
    author = serializers.SerializerMethodField()
    bulletin_title = serializers.CharField(source='bulletin.title', read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'subtitle', 'description',
            'bulletin_title', 'author', 'status', 'visibility',
            'likes_count', 'comments_count', 'created', 'published'
        ]
        read_only_fields = ['id', 'slug', 'created', 'published']

    def get_author(self, obj):
        """Return author info without full nested serializer."""
        return {
            'id': obj.author.id,
            'username': obj.author.user.username,
            'full_name': obj.author.full_name,
            'avatar_url': obj.author.avatar_url,
        }

    def get_likes_count(self, obj):
        """Count article likes."""
        return obj.likes.count()

    def get_comments_count(self, obj):
        """Count article comments."""
        return obj.comments.count()


class ArticleDetailSerializer(ArticleListSerializer):
    """
    Serializer for Article detail view.
    Extends list serializer to include full content and interaction flags.
    """
    content = serializers.CharField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + [
            'content', 'evaluation', 'updated',
            'is_liked', 'is_bookmarked', 'can_edit'
        ]

    def get_is_liked(self, obj):
        """Check if current user liked this article."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                author=request.user.profile,
                article=obj
            ).exists()
        return False

    def get_is_bookmarked(self, obj):
        """Check if current user bookmarked this article."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ReadLater.objects.filter(
                author=request.user.profile,
                article=obj
            ).exists()
        return False

    def get_can_edit(self, obj):
        """Check if current user can edit this article."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user.profile
        return False


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    Shows author details and allows create/update/delete.
    """
    author = ProfileSerializer(read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'author_name', 'article', 'content',
            'created', 'updated', 'can_edit'
        ]
        read_only_fields = ['id', 'author', 'created', 'updated']

    def get_can_edit(self, obj):
        """Check if current user can edit this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user.profile
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for Subscription model.
    Allows subscribing/unsubscribing to bulletins.
    """
    bulletin = BulletinListSerializer(read_only=True)
    bulletin_id = serializers.PrimaryKeyRelatedField(
        queryset=Bulletin.objects.all(),
        source='bulletin',
        write_only=True
    )

    class Meta:
        model = Subscription
        fields = ['id', 'bulletin', 'bulletin_id', 'created']
        read_only_fields = ['id', 'created']
