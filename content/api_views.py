from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from content.models import Article, Bulletin, Subscription
from content.serializers import (
    ArticleListSerializer, ArticleDetailSerializer,
    BulletinListSerializer, BulletinDetailSerializer,
    SubscriptionSerializer
)
from engagement.models import Like, ReadLater


class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for articles with full CRUD operations.

    ## Endpoints:
    - GET /api/v1/articles/ - List articles (paginated, filterable)
    - GET /api/v1/articles/{slug}/ - Get article detail
    - POST /api/v1/articles/ - Create article (writers only)
    - PUT/PATCH /api/v1/articles/{slug}/ - Update article (owner only)
    - DELETE /api/v1/articles/{slug}/ - Delete article (owner only)
    - POST /api/v1/articles/{slug}/like/ - Like/unlike article
    - POST /api/v1/articles/{slug}/bookmark/ - Bookmark/unbookmark article

    ## Filters:
    - status: Filter by draft/published
    - visibility: Filter by public/private
    - bulletin: Filter by bulletin ID

    ## Search:
    Search across title, subtitle, and content using ?search=keyword

    ## Ordering:
    Order by created, published, or title using ?ordering=-created
    """
    queryset = Article.objects.select_related('bulletin__owner').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'visibility', 'bulletin']
    search_fields = ['title', 'subtitle', 'content']
    ordering_fields = ['created', 'published', 'title']
    ordering = ['-created']
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Use detailed serializer for single article view."""
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def get_queryset(self):
        """
        Filter articles based on user role and authentication.

        - Anonymous: Only published public articles
        - Readers: Published public + subscribed private articles
        - Writers: Own articles + published public articles
        - Admins: All articles
        """
        queryset = super().get_queryset()

        # Non-authenticated users see only published public articles
        if not self.request.user.is_authenticated:
            return queryset.filter(status='published', visibility='public')

        user_profile = self.request.user.profile

        # Admins see everything
        if user_profile.is_admin:
            return queryset

        # Writers see their own + published public articles
        if user_profile.is_writer:
            return queryset.filter(
                Q(bulletin__owner=user_profile) |
                Q(status='published', visibility='public')
            )

        # Readers see public + subscribed private articles
        subscribed_bulletins = Subscription.objects.filter(
            subscriber=user_profile
        ).values_list('bulletin_id', flat=True)

        return queryset.filter(
            Q(status='published', visibility='public') |
            Q(status='published', visibility='private', bulletin_id__in=subscribed_bulletins)
        )

    def perform_create(self, serializer):
        """
        Create article with automatic bulletin assignment.
        Only writers can create articles.
        """
        if not self.request.user.profile.is_writer:
            raise PermissionError("Only writers can create articles")

        # Automatically set bulletin to writer's bulletin
        bulletin = self.request.user.profile.bulletin
        serializer.save(bulletin=bulletin)

    def perform_update(self, serializer):
        """Update article - only owner can update."""
        if serializer.instance.author != self.request.user.profile:
            raise PermissionError("You can only edit your own articles")
        serializer.save()

    def perform_destroy(self, instance):
        """Delete article - only owner can delete."""
        if instance.author != self.request.user.profile:
            raise PermissionError("You can only delete your own articles")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        """
        Like or unlike an article.

        If already liked, removes the like (toggle behavior).
        Returns: {"status": "liked"} or {"status": "unliked"}
        """
        article = self.get_object()
        like, created = Like.objects.get_or_create(
            author=request.user.profile,
            article=article
        )

        if not created:
            # Already liked, so unlike it
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, slug=None):
        """
        Add or remove article from read later list.

        If already bookmarked, removes the bookmark (toggle behavior).
        Returns: {"status": "bookmarked"} or {"status": "removed"}
        """
        article = self.get_object()
        bookmark, created = ReadLater.objects.get_or_create(
            author=request.user.profile,
            article=article
        )

        if not created:
            # Already bookmarked, so remove it
            bookmark.delete()
            return Response({'status': 'removed'}, status=status.HTTP_200_OK)

        return Response({'status': 'bookmarked'}, status=status.HTTP_201_CREATED)


class BulletinViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for bulletins (read-only).

    Bulletins are automatically created when a user becomes a writer.
    This endpoint allows browsing bulletins and subscribing to them.

    ## Endpoints:
    - GET /api/v1/bulletins/ - List bulletins
    - GET /api/v1/bulletins/{slug}/ - Get bulletin detail with recent articles
    - POST /api/v1/bulletins/{slug}/subscribe/ - Subscribe/unsubscribe

    ## Search:
    Search across title and description using ?search=keyword

    ## Ordering:
    Order by created or title using ?ordering=-created
    """
    queryset = Bulletin.objects.select_related('owner').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created', 'title']
    ordering = ['-created']
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Use detailed serializer for single bulletin view."""
        if self.action == 'retrieve':
            return BulletinDetailSerializer
        return BulletinListSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, slug=None):
        """
        Subscribe or unsubscribe to a bulletin.

        Writers cannot subscribe (they have their own bulletin).
        If already subscribed, unsubscribes (toggle behavior).
        Returns: {"status": "subscribed"} or {"status": "unsubscribed"}
        """
        bulletin = self.get_object()

        # Writers cannot subscribe (they have their own bulletin)
        if request.user.profile.is_writer:
            return Response(
                {'error': 'Writers cannot subscribe to bulletins'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription, created = Subscription.objects.get_or_create(
            subscriber=request.user.profile,
            bulletin=bulletin
        )

        if not created:
            # Already subscribed, so unsubscribe
            subscription.delete()
            return Response({'status': 'unsubscribed'}, status=status.HTTP_200_OK)

        return Response({'status': 'subscribed'}, status=status.HTTP_201_CREATED)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user subscriptions.

    Users can view their subscriptions, subscribe to new bulletins,
    and unsubscribe from existing ones.

    ## Endpoints:
    - GET /api/v1/subscriptions/ - List user's subscriptions
    - POST /api/v1/subscriptions/ - Subscribe to bulletin
    - DELETE /api/v1/subscriptions/{id}/ - Unsubscribe from bulletin
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only current user's subscriptions."""
        return Subscription.objects.filter(
            subscriber=self.request.user.profile
        ).select_related('bulletin__owner')

    def perform_create(self, serializer):
        """Create subscription with current user as subscriber."""
        serializer.save(subscriber=self.request.user.profile)
