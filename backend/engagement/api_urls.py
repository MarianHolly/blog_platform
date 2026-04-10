from django.urls import path, include
from rest_framework.routers import DefaultRouter
from engagement.api_views import CommentViewSet, ReadLaterViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register('comments', CommentViewSet, basename='comment')
router.register('bookmarks', ReadLaterViewSet, basename='bookmark')

# The router automatically creates these URL patterns:
#
# Comments:
#   GET    /comments/              -> List comments
#   POST   /comments/              -> Create comment
#   GET    /comments/{id}/         -> Get comment detail
#   PUT    /comments/{id}/         -> Update comment
#   PATCH  /comments/{id}/         -> Partial update
#   DELETE /comments/{id}/         -> Delete comment
#
# Bookmarks (ReadLater):
#   GET    /bookmarks/             -> List user's bookmarks
#   POST   /bookmarks/             -> Create bookmark
#   GET    /bookmarks/{id}/        -> Get bookmark detail
#   DELETE /bookmarks/{id}/        -> Delete bookmark

urlpatterns = router.urls
