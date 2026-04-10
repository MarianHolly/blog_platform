from django.urls import path, include
from rest_framework.routers import DefaultRouter
from content.api_views import ArticleViewSet, BulletinViewSet, SubscriptionViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='article')
router.register('bulletins', BulletinViewSet, basename='bulletin')
router.register('subscriptions', SubscriptionViewSet, basename='subscription')

# The router automatically creates these URL patterns:
#
# Articles:
#   GET    /articles/              -> List articles
#   POST   /articles/              -> Create article
#   GET    /articles/{slug}/       -> Get article detail
#   PUT    /articles/{slug}/       -> Update article
#   PATCH  /articles/{slug}/       -> Partial update
#   DELETE /articles/{slug}/       -> Delete article
#   POST   /articles/{slug}/like/  -> Like/unlike article
#   POST   /articles/{slug}/bookmark/ -> Bookmark article
#
# Bulletins:
#   GET    /bulletins/             -> List bulletins
#   GET    /bulletins/{slug}/      -> Get bulletin detail
#   POST   /bulletins/{slug}/subscribe/ -> Subscribe/unsubscribe
#
# Subscriptions:
#   GET    /subscriptions/         -> List user subscriptions
#   POST   /subscriptions/         -> Create subscription
#   DELETE /subscriptions/{id}/    -> Delete subscription

urlpatterns = router.urls
