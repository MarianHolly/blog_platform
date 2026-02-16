from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from engagement.models import Comment, ReadLater
from engagement.serializers import ReadLaterSerializer
from content.serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for comments with full CRUD operations.

    Users can comment on articles, edit their own comments,
    and delete their own comments.

    ## Endpoints:
    - GET /api/v1/comments/ - List all comments (filterable by article)
    - GET /api/v1/comments/{id}/ - Get comment detail
    - POST /api/v1/comments/ - Create comment
    - PUT/PATCH /api/v1/comments/{id}/ - Update own comment
    - DELETE /api/v1/comments/{id}/ - Delete own comment

    ## Filters:
    - article: Filter by article ID (?article=123)

    ## Permissions:
    - Must be authenticated to comment
    - Can only edit/delete own comments
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['article']

    def get_queryset(self):
        """
        Return all comments with related data pre-loaded.
        Uses select_related for performance optimization.
        """
        return Comment.objects.select_related('author', 'article').all()

    def perform_create(self, serializer):
        """
        Create comment with current user as author.
        The article must be specified in the request.
        """
        serializer.save(author=self.request.user.profile)

    def perform_update(self, serializer):
        """
        Update comment - only owner can update.
        Raises PermissionError if user is not the author.
        """
        if serializer.instance.author != self.request.user.profile:
            raise PermissionError("You can only edit your own comments")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete comment - only owner can delete.
        Raises PermissionError if user is not the author.
        """
        if instance.author != self.request.user.profile:
            raise PermissionError("You can only delete your own comments")
        instance.delete()


class ReadLaterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for read later bookmarks.

    Users can bookmark articles for later reading.
    The reading list is private to each user.

    ## Endpoints:
    - GET /api/v1/bookmarks/ - List user's bookmarked articles
    - POST /api/v1/bookmarks/ - Bookmark an article
    - DELETE /api/v1/bookmarks/{id}/ - Remove bookmark

    ## Permissions:
    - Must be authenticated
    - Can only see/manage own bookmarks

    ## Note:
    For quick toggle behavior, use the article bookmark action:
    POST /api/v1/articles/{slug}/bookmark/
    """
    serializer_class = ReadLaterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return only current user's bookmarks.
        Includes related article and bulletin data for performance.
        """
        return ReadLater.objects.filter(
            author=self.request.user.profile
        ).select_related('article__bulletin')

    def perform_create(self, serializer):
        """
        Create bookmark with current user as author.
        The article must be specified in the request.
        """
        serializer.save(author=self.request.user.profile)
