# Blog Platform Refactoring Roadmap

**Version**: 2.0
**Date**: 2026-02-16
**Goal**: Transform the blog platform into a medior-level professional portfolio project

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Three-Phase Development Strategy](#three-phase-development-strategy)
3. [Part 1: Critical Fixes + API Layer](#part-1-critical-fixes--api-layer-week-1)
4. [Part 2: Frontend Enhancements](#part-2-frontend-enhancements)
5. [Part 3: Backend Enhancements](#part-3-backend-enhancements)
6. [Deployment Guide: Hetzner + Coolify](#deployment-guide-hetzner--coolify)
7. [Development Workflow Optimization](#development-workflow-optimization)
8. [Testing Strategy](#testing-strategy)
9. [Quality Checklist](#quality-checklist)

---

## Overview

### Current State
- ✅ Solid Django foundation with PostgreSQL + Redis
- ✅ User roles: Reader, Writer, Admin
- ✅ Article management with evaluation workflow
- ✅ Engagement features (likes, comments, read later)
- ✅ 15 test files with good coverage
- ✅ Docker configuration
- ⚠️ Minor configuration bugs (easily fixable)

### Target State
- ✅ Modern REST API with Django REST Framework
- ✅ Professional, eye-catching UI
- ✅ Advanced features (tags, search, notifications, analytics)
- ✅ Async processing with Celery
- ✅ Production-ready deployment on Hetzner
- ✅ Comprehensive documentation

### Time Estimates
- **Part 1 (Critical + API)**: 15-20 hours (1 week)
- **Part 2 (Frontend)**: 35-45 hours (2-3 weeks part-time)
- **Part 3 (Backend)**: 45-60 hours (3-4 weeks part-time)
- **Total**: 95-125 hours

---

## Three-Phase Development Strategy

### 🎯 **Part 1: Critical Fixes + API Layer** → Deploy (Week 1)
**Focus**: Get production-ready with API
**Time**: 15-20 hours
**Outcome**: Deployable to Hetzner + Coolify

### 🎨 **Part 2: Frontend Enhancements** → Deploy (Flexible)
**Focus**: Visual redesign + UX improvements
**Time**: 35-45 hours
**Outcome**: Beautiful, professional UI

### ⚙️ **Part 3: Backend Enhancements** → Deploy (Flexible)
**Focus**: Advanced features + performance
**Time**: 45-60 hours
**Outcome**: Enterprise-level functionality

---

## Part 1: Critical Fixes + API Layer (Week 1)

**Goal**: Fix bugs, add REST API, deploy to production
**Time**: 15-20 hours
**Deadline**: 7 days from start

### 1.1 Critical Bug Fixes (30 minutes)

#### Task 1.1.1: Fix requirements.txt Encoding
**Time**: 5 minutes
**Priority**: 🔴 CRITICAL

**Issue**: File is UTF-16 encoded instead of UTF-8

**Fix**:
```bash
# Convert encoding
iconv -f UTF-16LE -t UTF-8 requirements.txt > requirements_utf8.txt
mv requirements_utf8.txt requirements.txt

# Or using dos2unix
dos2unix requirements.txt

# Verify
file requirements.txt  # Should show "UTF-8 Unicode text"
```

**Test**: `pip install -r requirements.txt` should work without errors

---

#### Task 1.1.2: Update CI/CD Python Versions
**Time**: 10 minutes
**Priority**: 🔴 CRITICAL

**Issue**: GitHub Actions tests Python 3.7-3.9, but Django 5.2 requires Python 3.10+

**Fix**: Edit `.github/workflows/django.yml`
```yaml
strategy:
  max-parallel: 4
  matrix:
    python-version: ["3.10", "3.11", "3.12"]  # Updated
```

**Test**: Push to GitHub and verify CI passes

---

#### Task 1.1.3: Add Article Slug Field
**Time**: 15 minutes
**Priority**: 🟡 HIGH

**Changes**: `content/models.py`
```python
from django.utils.text import slugify

class Article(Model):
    title = CharField(max_length=150)
    slug = SlugField(max_length=200, unique=True, blank=True)  # NEW
    # ... rest of fields

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # ... existing save logic
        super().save(*args, **kwargs)
```

**Migration**:
```bash
python manage.py makemigrations
python manage.py migrate
```

**Test**: Create article, verify slug is auto-generated

---

### 1.2 Django REST Framework Setup (12-15 hours)

#### Task 1.2.1: Install DRF Dependencies
**Time**: 30 minutes
**Priority**: 🔴 CRITICAL

**Add to requirements.txt** (after fixing encoding):
```txt
djangorestframework==3.15.2
djangorestframework-simplejwt==5.4.0
drf-spectacular==0.27.2
django-cors-headers==4.6.0
django-filter==24.3
```

**Install**:
```bash
pip install -r requirements.txt
```

**Update settings.py**:
```python
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    'django_filters',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add at top
    # ... existing middleware
]

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Blog Platform API',
    'DESCRIPTION': 'A modern content management API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS (for frontend development)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
]
if not DEBUG:
    # Add production frontend URL
    CORS_ALLOWED_ORIGINS.append('https://yourdomain.com')
```

---

#### Task 1.2.2: Create Serializers
**Time**: 3-4 hours
**Priority**: 🔴 CRITICAL

**Create**: `content/serializers.py`
```python
from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import Profile
from content.models import Article, Bulletin, Subscription
from engagement.models import Comment, Like, ReadLater


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
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
        return obj.get_articles_count()


class BulletinListSerializer(serializers.ModelSerializer):
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
        return obj.get_subscribers_count()

    def get_articles_count(self, obj):
        return obj.articles.filter(status='published').count()


class BulletinDetailSerializer(BulletinListSerializer):
    recent_articles = serializers.SerializerMethodField()

    class Meta(BulletinListSerializer.Meta):
        fields = BulletinListSerializer.Meta.fields + ['recent_articles']

    def get_recent_articles(self, obj):
        articles = obj.articles.filter(status='published')[:5]
        return ArticleListSerializer(articles, many=True).data


class ArticleListSerializer(serializers.ModelSerializer):
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
        return {
            'id': obj.author.id,
            'username': obj.author.user.username,
            'full_name': obj.author.full_name,
            'avatar_url': obj.author.avatar_url,
        }

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class ArticleDetailSerializer(ArticleListSerializer):
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
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                author=request.user.profile,
                article=obj
            ).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ReadLater.objects.filter(
                author=request.user.profile,
                article=obj
            ).exists()
        return False

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user.profile
        return False


class CommentSerializer(serializers.ModelSerializer):
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
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user.profile
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
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
```

**Create**: `engagement/serializers.py`
```python
from rest_framework import serializers
from engagement.models import Like, ReadLater


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'article', 'created']
        read_only_fields = ['id', 'created']


class ReadLaterSerializer(serializers.ModelSerializer):
    article_detail = serializers.SerializerMethodField()

    class Meta:
        model = ReadLater
        fields = ['id', 'article', 'article_detail', 'created']
        read_only_fields = ['id', 'created']

    def get_article_detail(self, obj):
        from content.serializers import ArticleListSerializer
        return ArticleListSerializer(obj.article).data
```

---

#### Task 1.2.3: Create API ViewSets
**Time**: 4-5 hours
**Priority**: 🔴 CRITICAL

**Create**: `content/api_views.py`
```python
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
    API endpoint for articles.

    list: Get paginated list of published articles
    retrieve: Get single article details
    create: Create new article (writers only)
    update: Update article (owner only)
    destroy: Delete article (owner only)

    Filters: status, visibility, bulletin
    Search: title, subtitle, content
    Ordering: created, published, title
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
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def get_queryset(self):
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
        # Only writers can create articles
        if not self.request.user.profile.is_writer:
            raise PermissionError("Only writers can create articles")

        # Automatically set bulletin to writer's bulletin
        bulletin = self.request.user.profile.bulletin
        serializer.save(bulletin=bulletin)

    def perform_update(self, serializer):
        # Only owner can update
        if serializer.instance.author != self.request.user.profile:
            raise PermissionError("You can only edit your own articles")
        serializer.save()

    def perform_destroy(self, instance):
        # Only owner can delete
        if instance.author != self.request.user.profile:
            raise PermissionError("You can only delete your own articles")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        """Like/unlike an article"""
        article = self.get_object()
        like, created = Like.objects.get_or_create(
            author=request.user.profile,
            article=article
        )

        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, slug=None):
        """Add/remove article from read later"""
        article = self.get_object()
        bookmark, created = ReadLater.objects.get_or_create(
            author=request.user.profile,
            article=article
        )

        if not created:
            bookmark.delete()
            return Response({'status': 'removed'}, status=status.HTTP_200_OK)

        return Response({'status': 'bookmarked'}, status=status.HTTP_201_CREATED)


class BulletinViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for bulletins (read-only).

    list: Get paginated list of bulletins
    retrieve: Get single bulletin with recent articles

    Search: title, description
    Ordering: created, title
    """
    queryset = Bulletin.objects.select_related('owner').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created', 'title']
    ordering = ['-created']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BulletinDetailSerializer
        return BulletinListSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, slug=None):
        """Subscribe/unsubscribe to bulletin"""
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
            subscription.delete()
            return Response({'status': 'unsubscribed'}, status=status.HTTP_200_OK)

        return Response({'status': 'subscribed'}, status=status.HTTP_201_CREATED)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user subscriptions.

    list: Get user's subscriptions
    create: Subscribe to bulletin
    destroy: Unsubscribe from bulletin
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(
            subscriber=self.request.user.profile
        ).select_related('bulletin__owner')

    def perform_create(self, serializer):
        serializer.save(subscriber=self.request.user.profile)
```

**Create**: `engagement/api_views.py`
```python
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from engagement.models import Comment, ReadLater
from engagement.serializers import ReadLaterSerializer
from content.serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for comments.

    list: Get all comments (filterable by article)
    create: Create comment
    update: Update own comment
    destroy: Delete own comment
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['article']

    def get_queryset(self):
        return Comment.objects.select_related('author', 'article').all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user.profile:
            raise PermissionError("You can only edit your own comments")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user.profile:
            raise PermissionError("You can only delete your own comments")
        instance.delete()


class ReadLaterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for read later bookmarks.

    list: Get user's bookmarked articles
    create: Bookmark article
    destroy: Remove bookmark
    """
    serializer_class = ReadLaterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReadLater.objects.filter(
            author=self.request.user.profile
        ).select_related('article__bulletin')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)
```

---

#### Task 1.2.4: Configure API URLs
**Time**: 30 minutes
**Priority**: 🔴 CRITICAL

**Create**: `content/api_urls.py`
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from content.api_views import ArticleViewSet, BulletinViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='article')
router.register('bulletins', BulletinViewSet, basename='bulletin')
router.register('subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = router.urls
```

**Create**: `engagement/api_urls.py`
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from engagement.api_views import CommentViewSet, ReadLaterViewSet

router = DefaultRouter()
router.register('comments', CommentViewSet, basename='comment')
router.register('bookmarks', ReadLaterViewSet, basename='bookmark')

urlpatterns = router.urls
```

**Update**: `blog_platform/urls.py`
```python
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Traditional Django views
    path('', include('content.urls')),
    path('accounts/', include('accounts.urls')),
    path('engagement/', include('engagement.urls')),

    # API v1
    path('api/v1/', include([
        # Authentication
        path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

        # Resources
        path('', include('content.api_urls')),
        path('', include('engagement.api_urls')),

        # Documentation
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ])),
]
```

---

#### Task 1.2.5: Create API Tests
**Time**: 3-4 hours
**Priority**: 🟡 HIGH

**Create**: `content/tests/test_api.py`
```python
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import Profile
from content.models import Article, Bulletin


class ArticleAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create writer
        self.writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        self.writer_profile = Profile.objects.get(user=self.writer_user)
        self.writer_profile.role = 'writer'
        self.writer_profile.save()

        # Create bulletin
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

        # Create article
        self.article = Article.objects.create(
            bulletin=self.bulletin,
            title='Test Article',
            slug='test-article',
            content='Test content',
            status='published',
            visibility='public'
        )

    def test_list_articles_unauthenticated(self):
        """Unauthenticated users can list public articles"""
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_article_by_slug(self):
        """Can retrieve article by slug"""
        response = self.client.get(f'/api/v1/articles/{self.article.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Article')

    def test_create_article_requires_auth(self):
        """Creating article requires authentication"""
        data = {
            'title': 'New Article',
            'content': 'New content',
            'status': 'draft'
        }
        response = self.client.post('/api/v1/articles/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_article_as_writer(self):
        """Writers can create articles"""
        self.client.force_authenticate(user=self.writer_user)
        data = {
            'title': 'New Article',
            'content': 'New content',
            'status': 'draft',
            'visibility': 'public'
        }
        response = self.client.post('/api/v1/articles/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 2)

    def test_like_article(self):
        """Authenticated users can like articles"""
        reader = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.client.force_authenticate(user=reader)

        response = self.client.post(f'/api/v1/articles/{self.article.slug}/like/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'liked')

        # Unlike
        response = self.client.post(f'/api/v1/articles/{self.article.slug}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unliked')


class BulletinAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        writer_profile = Profile.objects.get(user=writer_user)
        writer_profile.role = 'writer'
        writer_profile.save()

        self.bulletin = Bulletin.objects.create(
            owner=writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

    def test_list_bulletins(self):
        """Anyone can list bulletins"""
        response = self.client.get('/api/v1/bulletins/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_bulletin_by_slug(self):
        """Can retrieve bulletin by slug"""
        response = self.client.get(f'/api/v1/bulletins/{self.bulletin.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Bulletin')

    def test_subscribe_to_bulletin(self):
        """Readers can subscribe to bulletins"""
        reader = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.client.force_authenticate(user=reader)

        response = self.client.post(f'/api/v1/bulletins/{self.bulletin.slug}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'subscribed')
```

**Create**: `engagement/tests/test_api.py`
```python
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import Profile
from content.models import Article, Bulletin
from engagement.models import Comment


class CommentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create writer and article
        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        writer_profile = Profile.objects.get(user=writer_user)
        writer_profile.role = 'writer'
        writer_profile.save()

        bulletin = Bulletin.objects.create(
            owner=writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

        self.article = Article.objects.create(
            bulletin=bulletin,
            title='Test Article',
            slug='test-article',
            status='published',
            visibility='public'
        )

        # Create reader
        self.reader = User.objects.create_user('reader', 'reader@test.com', 'pass123')

    def test_create_comment(self):
        """Authenticated users can comment"""
        self.client.force_authenticate(user=self.reader)
        data = {
            'article': self.article.id,
            'content': 'Great article!'
        }
        response = self.client.post('/api/v1/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_list_article_comments(self):
        """Can filter comments by article"""
        Comment.objects.create(
            author=self.reader.profile,
            article=self.article,
            content='Test comment'
        )

        response = self.client.get(f'/api/v1/comments/?article={self.article.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
```

**Run tests**:
```bash
python manage.py test content.tests.test_api
python manage.py test engagement.tests.test_api
```

---

### 1.3 Mock Data Generator (4-5 hours)

#### Task 1.3.1: Install Faker
**Time**: 5 minutes

**Add to requirements.txt**:
```txt
Faker==28.4.1
```

**Install**:
```bash
pip install Faker
```

---

#### Task 1.3.2: Create Mock Data Command
**Time**: 3-4 hours
**Priority**: 🟡 HIGH

**Create**: `core/management/commands/generate_mock_data.py`
```python
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from faker import Faker

from accounts.models import Profile
from content.models import Article, Bulletin, Subscription
from engagement.models import Comment, Like, ReadLater


class Command(BaseCommand):
    help = 'Generate realistic mock data for the blog platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=30,
            help='Number of users to create (default: 30)'
        )
        parser.add_argument(
            '--articles',
            type=int,
            default=50,
            help='Number of articles to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating'
        )

    def handle(self, *args, **options):
        fake = Faker()

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Data cleared'))

        num_users = options['users']
        num_articles = options['articles']

        # Calculate distributions
        num_writers = int(num_users * 0.2)  # 20% writers
        num_readers = num_users - num_writers

        self.stdout.write(f'Generating {num_users} users ({num_writers} writers, {num_readers} readers)...')

        # Create readers
        readers = []
        for i in range(num_readers):
            username = fake.user_name()
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = fake.user_name()

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='password123'
            )

            profile = user.profile
            profile.role = 'reader'
            profile.biography = fake.text(max_nb_chars=200) if random.random() > 0.3 else ''
            profile.save()

            readers.append(profile)

            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Created {i + 1} readers...')

        self.stdout.write(self.style.SUCCESS(f'Created {num_readers} readers'))

        # Create writers with bulletins
        writers = []
        bulletins = []
        for i in range(num_writers):
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = fake.user_name()

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='password123'
            )

            profile = user.profile
            profile.role = 'writer'
            profile.biography = fake.text(max_nb_chars=300)
            profile.save()

            # Create bulletin
            bulletin_title = fake.catch_phrase()
            bulletin = Bulletin.objects.create(
                owner=profile,
                title=bulletin_title,
                slug=slugify(bulletin_title),
                description=fake.text(max_nb_chars=200)
            )

            writers.append(profile)
            bulletins.append(bulletin)

            if (i + 1) % 5 == 0:
                self.stdout.write(f'  Created {i + 1} writers with bulletins...')

        self.stdout.write(self.style.SUCCESS(f'Created {num_writers} writers with bulletins'))

        # Create subscriptions (readers subscribe to random bulletins)
        self.stdout.write('Creating subscriptions...')
        subscription_count = 0
        for reader in readers:
            # Each reader subscribes to 2-5 random bulletins
            num_subs = random.randint(2, min(5, len(bulletins)))
            selected_bulletins = random.sample(bulletins, num_subs)

            for bulletin in selected_bulletins:
                Subscription.objects.get_or_create(
                    subscriber=reader,
                    bulletin=bulletin
                )
                subscription_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {subscription_count} subscriptions'))

        # Create articles
        self.stdout.write(f'Generating {num_articles} articles...')
        articles = []

        for i in range(num_articles):
            bulletin = random.choice(bulletins)

            title = fake.sentence(nb_words=6).rstrip('.')

            # Generate article content (multiple paragraphs)
            paragraphs = [f'<p>{fake.paragraph(nb_sentences=random.randint(3, 8))}</p>'
                         for _ in range(random.randint(5, 15))]
            content = '\n'.join(paragraphs)

            # 80% published, 20% draft
            status = 'published' if random.random() > 0.2 else 'draft'

            # 90% public, 10% private
            visibility = 'public' if random.random() > 0.1 else 'private'

            # Random evaluation
            if status == 'published':
                evaluation = random.choice(['approved', 'approved', 'approved', 'pending'])
            else:
                evaluation = 'pending'

            article = Article.objects.create(
                bulletin=bulletin,
                title=title,
                slug=slugify(title),
                subtitle=fake.sentence() if random.random() > 0.3 else '',
                description=fake.text(max_nb_chars=150) if random.random() > 0.5 else '',
                content=content,
                status=status,
                visibility=visibility,
                evaluation=evaluation
            )

            articles.append(article)

            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Created {i + 1} articles...')

        published_articles = [a for a in articles if a.status == 'published']
        self.stdout.write(self.style.SUCCESS(f'Created {num_articles} articles ({len(published_articles)} published)'))

        # Create engagement (likes, comments, bookmarks)
        self.stdout.write('Creating engagement data...')

        like_count = 0
        comment_count = 0
        bookmark_count = 0

        for article in published_articles:
            # Random number of likes (0-15)
            num_likes = random.randint(0, min(15, len(readers)))
            for reader in random.sample(readers, num_likes):
                Like.objects.get_or_create(author=reader, article=article)
                like_count += 1

            # Random number of comments (0-5)
            num_comments = random.randint(0, min(5, len(readers)))
            for reader in random.sample(readers, num_comments):
                try:
                    Comment.objects.create(
                        author=reader,
                        article=article,
                        content=fake.text(max_nb_chars=200)
                    )
                    comment_count += 1
                except:
                    # Skip if already commented (unique constraint)
                    pass

            # Random bookmarks (0-8)
            num_bookmarks = random.randint(0, min(8, len(readers)))
            for reader in random.sample(readers, num_bookmarks):
                ReadLater.objects.get_or_create(author=reader, article=article)
                bookmark_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {like_count} likes, {comment_count} comments, {bookmark_count} bookmarks'
        ))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== DATA GENERATION COMPLETE ==='))
        self.stdout.write(f'Users: {num_users} ({num_readers} readers, {num_writers} writers)')
        self.stdout.write(f'Bulletins: {len(bulletins)}')
        self.stdout.write(f'Articles: {num_articles} ({len(published_articles)} published)')
        self.stdout.write(f'Subscriptions: {subscription_count}')
        self.stdout.write(f'Likes: {like_count}')
        self.stdout.write(f'Comments: {comment_count}')
        self.stdout.write(f'Bookmarks: {bookmark_count}')
        self.stdout.write('\nDefault password for all users: password123')
```

**Create the directory if needed**:
```bash
mkdir -p core/management/commands
touch core/management/__init__.py
touch core/management/commands/__init__.py
```

**Usage**:
```bash
# Generate default data (30 users, 50 articles)
python manage.py generate_mock_data

# Generate more data
python manage.py generate_mock_data --users 100 --articles 200

# Clear and regenerate
python manage.py generate_mock_data --clear
```

---

### 1.4 Documentation & Polish (2 hours)

#### Task 1.4.1: Update README.md
**Time**: 1 hour

Add API documentation section:
```markdown
## API Documentation

The platform provides a RESTful API for all resources.

### Base URL
```
http://localhost:8000/api/v1/
```

### Authentication
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token in requests
curl http://localhost:8000/api/v1/articles/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Interactive Documentation
Visit http://localhost:8000/api/v1/docs/ for interactive Swagger UI

### Endpoints
- `GET /api/v1/articles/` - List articles
- `GET /api/v1/articles/{slug}/` - Get article details
- `POST /api/v1/articles/` - Create article (writers only)
- `POST /api/v1/articles/{slug}/like/` - Like/unlike article
- `POST /api/v1/articles/{slug}/bookmark/` - Bookmark article
- `GET /api/v1/bulletins/` - List bulletins
- `POST /api/v1/bulletins/{slug}/subscribe/` - Subscribe to bulletin
- `GET /api/v1/comments/` - List comments
- `POST /api/v1/comments/` - Create comment
- `GET /api/v1/bookmarks/` - List bookmarked articles
```

---

#### Task 1.4.2: Create API Postman Collection
**Time**: 1 hour

Export Swagger schema and create Postman collection for testing.

---

### ✅ Part 1 Completion Checklist

Before deploying to Hetzner:

- [ ] requirements.txt is UTF-8 encoded
- [ ] CI/CD tests pass with Python 3.10+
- [ ] Article model has slug field
- [ ] Django REST Framework installed and configured
- [ ] All serializers created
- [ ] All API viewsets created and working
- [ ] API URLs configured correctly
- [ ] JWT authentication working
- [ ] API tests pass (minimum 80% coverage)
- [ ] Mock data generator works
- [ ] API documentation accessible at /api/v1/docs/
- [ ] README.md updated with API docs
- [ ] All migrations applied
- [ ] No security vulnerabilities (run `safety check`)

**Test commands**:
```bash
# Run all tests
python manage.py test

# Check coverage
coverage run --source='.' manage.py test
coverage report

# Generate mock data
python manage.py generate_mock_data --users 50 --articles 100

# Start server and test API
python manage.py runserver
# Visit http://localhost:8000/api/v1/docs/
```

---

## Deployment Guide: Hetzner + Coolify

### Why Hetzner + Coolify?
- **Cost-effective**: ~€5/month for VPS vs Railway's pricing
- **Full control**: Root access to server
- **Coolify**: Open-source Heroku/Netlify alternative with nice UI
- **European data**: GDPR-compliant hosting

### Prerequisites
- Hetzner account
- Domain name (optional but recommended)
- GitHub repository

---

### Step 1: Create Hetzner VPS (15 minutes)

1. **Go to** [Hetzner Cloud](https://www.hetzner.com/cloud)
2. **Create project**: "blog-platform"
3. **Create server**:
   - **Location**: Nuremberg, Germany (or nearest)
   - **Image**: Ubuntu 24.04
   - **Type**: CPX11 (2 vCPU, 2GB RAM) - €4.51/month
   - **Networking**: Enable IPv4 + IPv6
   - **SSH Key**: Add your SSH public key
   - **Firewall**: Create firewall with these rules:
     - SSH (22) - Your IP only
     - HTTP (80) - 0.0.0.0/0
     - HTTPS (443) - 0.0.0.0/0
4. **Create server** and note the IP address

---

### Step 2: Install Coolify (20 minutes)

**SSH into server**:
```bash
ssh root@YOUR_SERVER_IP
```

**Install Coolify** (one-line install):
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

This installs:
- Docker
- Docker Compose
- Coolify
- Traefik (reverse proxy)
- PostgreSQL (for Coolify itself)

**Wait 5-10 minutes** for installation to complete.

**Access Coolify**:
1. Open browser: `http://YOUR_SERVER_IP:8000`
2. Create admin account
3. Login to Coolify dashboard

---

### Step 3: Configure Domain (Optional, 10 minutes)

If you have a domain:

1. **Add DNS A record**:
   ```
   blog.yourdomain.com → YOUR_SERVER_IP
   api.yourdomain.com → YOUR_SERVER_IP
   ```

2. **In Coolify**:
   - Go to Settings → Domains
   - Add domain: `blog.yourdomain.com`
   - Enable SSL (Let's Encrypt auto-configured)

---

### Step 4: Deploy Application (30 minutes)

#### 4.1 Create New Application in Coolify

1. **Click** "New Resource" → "Application"
2. **Select** "Public Repository"
3. **Enter repo URL**: `https://github.com/yourusername/blog_platform`
4. **Branch**: `dev` (or `main`)
5. **Build Pack**: Dockerfile

#### 4.2 Configure Environment Variables

In Coolify, go to your app → Environment Variables:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=blog.yourdomain.com,YOUR_SERVER_IP
CSRF_TRUSTED_ORIGINS=https://blog.yourdomain.com

# Database (Coolify provides PostgreSQL)
DATABASE_URL=postgresql://user:password@postgres:5432/blog_platform

# Redis (Coolify provides Redis)
REDIS_URL=redis://redis:6379/0

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-secret

# Superuser (for first deployment)
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@yourdomain.com
SUPERUSER_PASSWORD=secure-password-here
```

#### 4.3 Add PostgreSQL Database

1. **In Coolify**: Resources → New Resource → Database
2. **Select**: PostgreSQL 17
3. **Name**: blog-platform-db
4. **Create**
5. **Copy connection string** and use in `DATABASE_URL`

#### 4.4 Add Redis

1. **In Coolify**: Resources → New Resource → Database
2. **Select**: Redis
3. **Name**: blog-platform-redis
4. **Create**
5. **Copy connection string** and use in `REDIS_URL`

#### 4.5 Configure Build Settings

**Create**: `nixpacks.toml` in project root:
```toml
[phases.setup]
nixPkgs = ['python310', 'postgresql']

[phases.install]
cmds = ['pip install -r requirements.txt']

[phases.build]
cmds = [
  'python manage.py collectstatic --noinput',
  'python manage.py migrate'
]

[start]
cmd = 'gunicorn blog_platform.wsgi:application --bind 0.0.0.0:8000 --workers 3'
```

**Or use Dockerfile** (already exists in your project):

Update `Dockerfile` if needed:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "blog_platform.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

#### 4.6 Add Health Check

**Create**: `healthcheck.py` in project root:
```python
#!/usr/bin/env python
import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_platform.settings')
django.setup()

from django.db import connection

try:
    connection.ensure_connection()
    print("OK")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
```

In Coolify → Application → Health Check:
```
/health/  (or custom endpoint)
```

#### 4.7 Deploy

1. **Click** "Deploy" in Coolify
2. **Monitor** build logs
3. **Wait** for deployment (5-10 minutes first time)

---

### Step 5: Post-Deployment Tasks (20 minutes)

**SSH into server and access container**:
```bash
# Find container ID
docker ps

# Enter container
docker exec -it CONTAINER_ID bash

# Inside container:
python manage.py createsuperuser
python manage.py generate_mock_data --users 50 --articles 100
```

**Or use Coolify's Execute Command**:
- Go to application → Terminal
- Run commands directly

---

### Step 6: Setup CI/CD with GitHub Actions (Optional, 30 minutes)

**Create**: `.github/workflows/deploy.yml`
```yaml
name: Deploy to Hetzner

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Deploy to Coolify
      uses: fjogeleit/http-request-action@v1
      with:
        url: 'https://YOUR_COOLIFY_URL/api/v1/deploy'
        method: 'POST'
        customHeaders: '{"Authorization": "Bearer ${{ secrets.COOLIFY_TOKEN }}"}'
```

**Get Coolify API token**:
- Coolify → Settings → API Tokens → Create

**Add to GitHub Secrets**:
- Repository → Settings → Secrets → New secret
- Name: `COOLIFY_TOKEN`
- Value: Your Coolify API token

---

### Deployment Checklist

- [ ] Hetzner VPS created and accessible
- [ ] Coolify installed and accessible
- [ ] Domain configured (if using)
- [ ] SSL certificate active
- [ ] PostgreSQL database created in Coolify
- [ ] Redis created in Coolify
- [ ] Environment variables configured
- [ ] Application deployed successfully
- [ ] Health check passing
- [ ] Static files loading
- [ ] Admin panel accessible
- [ ] API accessible at /api/v1/
- [ ] API docs accessible at /api/v1/docs/
- [ ] Mock data generated
- [ ] Superuser account created
- [ ] Database backups configured in Coolify

---

### Monitoring & Maintenance

**Coolify provides**:
- Application logs
- Resource usage (CPU, RAM, disk)
- Deployment history
- Automatic SSL renewal
- Database backups

**Recommended additions**:
1. **Uptime monitoring**: UptimeRobot (free)
2. **Error tracking**: Sentry (free tier)
3. **Analytics**: Plausible or Google Analytics

---

### Estimated Costs

| Service | Cost/Month | Notes |
|---------|------------|-------|
| Hetzner VPS (CPX11) | €4.51 | 2 vCPU, 2GB RAM, 40GB SSD |
| Cloudinary | €0 | Free tier: 25GB storage, 25GB bandwidth |
| Domain | €10-15/year | One-time annual cost |
| **Total** | **~€5/month** | vs Railway's €20+/month |

---

## Part 2: Frontend Enhancements

**Goal**: Create a professional, eye-catching UI
**Time**: 35-45 hours
**Flexibility**: Pick tasks based on energy level

### Frontend Task Categories

#### 🟢 **Easy Tasks** (1-2 hours each) - Low energy days
#### 🟡 **Medium Tasks** (3-4 hours each) - Normal energy days
#### 🔴 **Hard Tasks** (5-8 hours each) - High energy days

---

### 2.1 Design System & Foundation

#### 🟢 Task 2.1.1: Define Color Palette
**Time**: 1 hour
**Energy**: Low

Create modern, professional color scheme:
```css
/* static/css/variables.css */
:root {
  /* Primary colors */
  --color-primary-50: #f0f9ff;
  --color-primary-100: #e0f2fe;
  --color-primary-200: #bae6fd;
  --color-primary-500: #0ea5e9;
  --color-primary-600: #0284c7;
  --color-primary-700: #0369a1;

  /* Neutral colors */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-500: #6b7280;
  --color-gray-700: #374151;
  --color-gray-900: #111827;

  /* Semantic colors */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-serif: 'Merriweather', Georgia, serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Spacing */
  --spacing-xs: 0.5rem;
  --spacing-sm: 0.75rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;

  /* Borders */
  --border-radius-sm: 0.375rem;
  --border-radius-md: 0.5rem;
  --border-radius-lg: 0.75rem;
  --border-radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: var(--color-gray-900);
    --color-text: var(--color-gray-100);
  }
}
```

**Load Google Fonts** in `base.html`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Merriweather:wght@300;400;700&display=swap" rel="stylesheet">
```

---

#### 🟢 Task 2.1.2: Create Component Library Base
**Time**: 2 hours
**Energy**: Low

**Create**: `static/css/components.css`
```css
/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-weight: 500;
  border-radius: var(--border-radius-md);
  transition: all 0.2s;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--color-primary-600);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: var(--color-gray-200);
  color: var(--color-gray-700);
}

.btn-outline {
  background: transparent;
  border: 2px solid var(--color-primary-600);
  color: var(--color-primary-600);
}

/* Cards */
.card {
  background: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-lg);
  transition: all 0.3s;
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

/* Badges */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--border-radius-full);
}

.badge-success {
  background: var(--color-success);
  color: white;
}

.badge-warning {
  background: var(--color-warning);
  color: white;
}

/* Inputs */
.input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid var(--color-gray-300);
  border-radius: var(--border-radius-md);
  font-size: 1rem;
  transition: all 0.2s;
}

.input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}
```

---

#### 🟡 Task 2.1.3: Design Homepage Hero Section
**Time**: 3 hours
**Energy**: Medium

**Update**: `templates/content/home.html`
```html
{% extends 'base.html' %}

{% block content %}
<!-- Hero Section -->
<section class="hero">
  <div class="hero-content">
    <h1 class="hero-title">
      Discover Stories That Matter
    </h1>
    <p class="hero-subtitle">
      Join our community of writers and readers sharing insights,
      experiences, and knowledge across diverse topics.
    </p>
    <div class="hero-cta">
      {% if user.is_authenticated %}
        <a href="{% url 'article_list' %}" class="btn btn-primary btn-lg">
          Explore Articles
        </a>
      {% else %}
        <a href="{% url 'signup' %}" class="btn btn-primary btn-lg">
          Start Reading
        </a>
        <a href="{% url 'login' %}" class="btn btn-outline btn-lg">
          Sign In
        </a>
      {% endif %}
    </div>
  </div>

  <!-- Hero Image/Illustration -->
  <div class="hero-visual">
    <img src="{% static 'images/hero-illustration.svg' %}" alt="Reading illustration">
  </div>
</section>

<!-- Stats Section -->
<section class="stats">
  <div class="container">
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-number">{{ total_articles|default:"0" }}</div>
        <div class="stat-label">Articles Published</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ total_writers|default:"0" }}</div>
        <div class="stat-label">Active Writers</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ total_readers|default:"0" }}</div>
        <div class="stat-label">Engaged Readers</div>
      </div>
    </div>
  </div>
</section>

<!-- Featured Articles Grid -->
<section class="featured-articles">
  <div class="container">
    <h2 class="section-title">Latest Articles</h2>

    <div class="articles-grid">
      {% for article in featured_articles %}
        <article class="article-card">
          {% if article.featured_image %}
            <img src="{{ article.featured_image.url }}" class="article-image" alt="{{ article.title }}">
          {% else %}
            <div class="article-image-placeholder">
              <span>{{ article.title|slice:":1" }}</span>
            </div>
          {% endif %}

          <div class="article-content">
            <div class="article-meta">
              <img src="{{ article.author.avatar_url }}" class="author-avatar" alt="{{ article.author.full_name }}">
              <div>
                <span class="author-name">{{ article.author.full_name }}</span>
                <span class="article-date">{{ article.published|date:"M d, Y" }}</span>
              </div>
            </div>

            <h3 class="article-title">
              <a href="{% url 'article_detail' article.slug %}">{{ article.title }}</a>
            </h3>

            {% if article.description %}
              <p class="article-description">{{ article.description }}</p>
            {% endif %}

            <div class="article-footer">
              <div class="article-stats">
                <span>❤️ {{ article.likes.count }}</span>
                <span>💬 {{ article.comments.count }}</span>
              </div>
              <span class="read-time">5 min read</span>
            </div>
          </div>
        </article>
      {% endfor %}
    </div>
  </div>
</section>

<!-- Popular Writers -->
<section class="popular-writers">
  <div class="container">
    <h2 class="section-title">Featured Writers</h2>

    <div class="writers-grid">
      {% for writer in recent_writers %}
        <div class="writer-card">
          <img src="{{ writer.avatar_url }}" class="writer-avatar" alt="{{ writer.full_name }}">
          <h3 class="writer-name">{{ writer.full_name }}</h3>
          <p class="writer-bio">{{ writer.biography|truncatewords:20 }}</p>
          <div class="writer-stats">
            <span>{{ writer.get_articles_count }} articles</span>
            <span>{{ writer.bulletin.subscribers.count }} subscribers</span>
          </div>
          <a href="{% url 'bulletin_detail' writer.bulletin.slug %}" class="btn btn-outline btn-sm">
            View Profile
          </a>
        </div>
      {% endfor %}
    </div>
  </div>
</section>
{% endblock %}
```

**Create**: `static/css/home.css`
```css
/* Hero Section */
.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  padding: 6rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
  align-items: center;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--color-gray-600);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.hero-cta {
  display: flex;
  gap: 1rem;
}

/* Stats Section */
.stats {
  background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-700));
  padding: 3rem 2rem;
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.stat-number {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  opacity: 0.9;
}

/* Articles Grid */
.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.article-card {
  background: white;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s;
}

.article-card:hover {
  box-shadow: var(--shadow-xl);
  transform: translateY(-4px);
}

.article-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.article-image-placeholder {
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  color: white;
  font-weight: 700;
}

.article-content {
  padding: 1.5rem;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.author-name {
  display: block;
  font-weight: 600;
  font-size: 0.875rem;
}

.article-date {
  display: block;
  font-size: 0.75rem;
  color: var(--color-gray-500);
}

.article-title a {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-gray-900);
  text-decoration: none;
  display: block;
  margin-bottom: 0.75rem;
  line-height: 1.3;
}

.article-title a:hover {
  color: var(--color-primary-600);
}

.article-description {
  color: var(--color-gray-600);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.article-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--color-gray-200);
}

.article-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

@media (max-width: 768px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 3rem 1rem;
  }

  .hero-visual {
    display: none;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .articles-grid {
    grid-template-columns: 1fr;
  }
}
```

---

### 2.2 Article Pages

#### 🔴 Task 2.2.1: Redesign Article Detail Page
**Time**: 6 hours
**Energy**: High

Modern article reading experience with:
- Beautiful typography
- Reading progress indicator
- Floating share buttons
- Related articles sidebar
- Comment section redesign

**Update**: `templates/content/article_detail.html`
```html
{% extends 'base.html' %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/article-detail.css' %}">
{% endblock %}

{% block content %}
<!-- Reading Progress Bar -->
<div class="reading-progress-bar" id="readingProgress"></div>

<article class="article-container">
  <!-- Article Header -->
  <header class="article-header">
    <div class="article-meta-top">
      <a href="{% url 'bulletin_detail' article.bulletin.slug %}" class="bulletin-link">
        {{ article.bulletin.title }}
      </a>
      <span class="article-date">{{ article.published|date:"F d, Y" }}</span>
    </div>

    <h1 class="article-title">{{ article.title }}</h1>

    {% if article.subtitle %}
      <p class="article-subtitle">{{ article.subtitle }}</p>
    {% endif %}

    <div class="author-info">
      <img src="{{ article.author.avatar_url }}" class="author-avatar-large" alt="{{ article.author.full_name }}">
      <div>
        <a href="{% url 'profile' article.author.id %}" class="author-name-large">
          {{ article.author.full_name }}
        </a>
        <div class="author-stats">
          {{ article.author.get_articles_count }} articles ·
          {{ article.author.bulletin.subscribers.count }} subscribers
        </div>
      </div>

      {% if user.is_authenticated and user.profile != article.author %}
        <button class="btn btn-primary follow-btn" data-bulletin="{{ article.bulletin.slug }}">
          {% if is_subscribed %}Unsubscribe{% else %}Subscribe{% endif %}
        </button>
      {% endif %}
    </div>
  </header>

  <!-- Article Content -->
  <div class="article-body">
    {{ article.content|safe }}
  </div>

  <!-- Article Footer -->
  <footer class="article-footer">
    <div class="article-tags">
      {% for tag in article.tags.all %}
        <a href="{% url 'tag_detail' tag.slug %}" class="tag">{{ tag.name }}</a>
      {% endfor %}
    </div>

    <div class="article-actions">
      <button class="action-btn {% if is_liked %}active{% endif %}" data-action="like" data-slug="{{ article.slug }}">
        <svg><!-- Heart icon --></svg>
        <span class="count">{{ article.likes.count }}</span>
      </button>

      <button class="action-btn" data-action="comment">
        <svg><!-- Comment icon --></svg>
        <span class="count">{{ article.comments.count }}</span>
      </button>

      <button class="action-btn {% if is_bookmarked %}active{% endif %}" data-action="bookmark" data-slug="{{ article.slug }}">
        <svg><!-- Bookmark icon --></svg>
      </button>

      <button class="action-btn" data-action="share">
        <svg><!-- Share icon --></svg>
      </button>
    </div>
  </footer>

  <!-- Comments Section -->
  <section class="comments-section">
    <h2 class="section-title">Comments ({{ article.comments.count }})</h2>

    {% if user.is_authenticated %}
      <form class="comment-form" method="post" action="{% url 'create_comment' article.id %}">
        {% csrf_token %}
        <img src="{{ user.profile.avatar_url }}" class="commenter-avatar" alt="{{ user.username }}">
        <div class="comment-input-wrapper">
          {{ comment_form.content }}
          <button type="submit" class="btn btn-primary">Post Comment</button>
        </div>
      </form>
    {% else %}
      <p class="login-prompt">
        <a href="{% url 'login' %}">Sign in</a> to join the discussion
      </p>
    {% endif %}

    <div class="comments-list">
      {% for comment in article.comments.all %}
        <div class="comment">
          <img src="{{ comment.author.avatar_url }}" class="commenter-avatar" alt="{{ comment.author.full_name }}">
          <div class="comment-content">
            <div class="comment-header">
              <span class="commenter-name">{{ comment.author.full_name }}</span>
              <span class="comment-date">{{ comment.created|timesince }} ago</span>
            </div>
            <p class="comment-text">{{ comment.content }}</p>
          </div>
        </div>
      {% endfor %}
    </div>
  </section>
</article>

<!-- Sidebar (for larger screens) -->
<aside class="article-sidebar">
  <!-- Author Bio -->
  <div class="sidebar-card">
    <h3>About the Author</h3>
    <img src="{{ article.author.avatar_url }}" class="author-avatar-large" alt="{{ article.author.full_name }}">
    <h4>{{ article.author.full_name }}</h4>
    <p>{{ article.author.biography|truncatewords:30 }}</p>
  </div>

  <!-- Related Articles -->
  <div class="sidebar-card">
    <h3>More from {{ article.author.full_name }}</h3>
    {% for related in related_articles %}
      <a href="{% url 'article_detail' related.slug %}" class="related-article">
        <h4>{{ related.title }}</h4>
        <span class="related-date">{{ related.published|date:"M d" }}</span>
      </a>
    {% endfor %}
  </div>
</aside>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/article-interactions.js' %}"></script>
{% endblock %}
```

**Create**: `static/js/article-interactions.js`
```javascript
// Reading progress bar
window.addEventListener('scroll', () => {
  const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
  const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  const scrolled = (winScroll / height) * 100;
  document.getElementById('readingProgress').style.width = scrolled + '%';
});

// Like/Bookmark AJAX
document.querySelectorAll('.action-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    const action = btn.dataset.action;
    const slug = btn.dataset.slug;

    if (!slug) return;

    try {
      const response = await fetch(`/api/v1/articles/${slug}/${action}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok) {
        btn.classList.toggle('active');
        if (action === 'like') {
          const count = btn.querySelector('.count');
          count.textContent = parseInt(count.textContent) + (btn.classList.contains('active') ? 1 : -1);
        }
      }
    } catch (error) {
      console.error('Action failed:', error);
    }
  });
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}
```

---

### 2.3 Dashboard & User Pages

#### 🟡 Task 2.3.1: Writer Dashboard Redesign
**Time**: 4 hours
**Energy**: Medium

Modern dashboard with:
- Analytics charts
- Recent articles table
- Quick actions
- Subscriber growth

#### 🟢 Task 2.3.2: Profile Page Enhancement
**Time**: 2 hours
**Energy**: Low

Improve user profile display with better layout and stats.

---

### 2.4 Navigation & Layout

#### 🟢 Task 2.4.1: Modern Navbar
**Time**: 2 hours
**Energy**: Low

Sticky navbar with:
- Logo
- Search bar
- User menu dropdown
- Notifications badge
- Mobile hamburger menu

#### 🟢 Task 2.4.2: Footer Redesign
**Time**: 1 hour
**Energy**: Low

Professional footer with:
- Site links
- Social media
- Newsletter signup
- Copyright

---

### 2.5 Interactive Elements

#### 🟡 Task 2.5.1: Add Loading States
**Time**: 3 hours
**Energy**: Medium

Add skeleton screens and spinners for better UX.

#### 🟡 Task 2.5.2: Add Micro-interactions
**Time**: 3 hours
**Energy**: Medium

Hover effects, transitions, animations using CSS/JS.

---

### 2.6 Mobile Optimization

#### 🔴 Task 2.6.1: Full Mobile Responsiveness
**Time**: 6 hours
**Energy**: High

Ensure all pages work perfectly on mobile:
- Responsive grids
- Touch-friendly buttons
- Mobile navigation
- Optimized images

---

## Part 3: Backend Enhancements

**Goal**: Add advanced features and optimize performance
**Time**: 45-60 hours
**Flexibility**: Pick tasks based on focus level

### Backend Task Categories

#### 🟢 **Easy Tasks** (2-3 hours each) - Learning mode
#### 🟡 **Medium Tasks** (4-6 hours each) - Focused work
#### 🔴 **Hard Tasks** (6-10 hours each) - Deep focus required

---

### 3.1 Tagging System

#### 🟡 Task 3.1.1: Create Tag Models
**Time**: 4 hours
**Energy**: Medium
**Focus**: Database design

**Create**: `content/models.py` additions
```python
class Tag(Model):
    name = CharField(max_length=50, unique=True)
    slug = SlugField(unique=True, max_length=60)
    description = TextField(max_length=200, blank=True)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_articles_count(self):
        return self.articles.filter(status='published').count()


# Update Article model
class Article(Model):
    # ... existing fields
    tags = ManyToManyField(Tag, related_name='articles', blank=True)
```

**Migration**:
```bash
python manage.py makemigrations
python manage.py migrate
```

**Admin**:
```python
# content/admin.py
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'get_articles_count', 'created']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
```

**Views & URLs**: Create tag detail page, tag cloud, tag autocomplete.

---

### 3.2 Full-Text Search

#### 🔴 Task 3.2.1: PostgreSQL Full-Text Search
**Time**: 6 hours
**Energy**: High
**Focus**: Learning PostgreSQL features

**Install SearchVector**:
```python
# content/models.py
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.indexes import GinIndex

class Article(Model):
    # ... existing fields

    class Meta:
        indexes = [
            GinIndex(fields=['title', 'content'], name='article_search_idx'),
        ]
```

**Create search view**:
```python
# content/views.py
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

class ArticleSearchView(ListView):
    model = Article
    template_name = 'content/search_results.html'
    context_object_name = 'articles'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '')

        if not query:
            return Article.objects.none()

        search_vector = SearchVector('title', weight='A') + \
                       SearchVector('subtitle', weight='B') + \
                       SearchVector('content', weight='C')

        search_query = SearchQuery(query)

        return Article.objects.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(
            rank__gte=0.01,
            status='published'
        ).order_by('-rank')
```

**Add to API**:
```python
# content/api_views.py
from rest_framework.decorators import action
from rest_framework.response import Response

class ArticleViewSet(viewsets.ModelViewSet):
    # ... existing code

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')

        if not query:
            return Response([])

        # Use the same search logic
        results = self.get_queryset().annotate(
            rank=SearchRank(SearchVector('title', 'content'), SearchQuery(query))
        ).filter(rank__gte=0.01).order_by('-rank')[:20]

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
```

---

### 3.3 Notification System

#### 🔴 Task 3.3.1: Create Notification Models
**Time**: 8 hours
**Energy**: High
**Focus**: Complex relationships

**Create new app**:
```bash
python manage.py startapp notifications
```

**Models**:
```python
# notifications/models.py
from django.db.models import *
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(Model):
    TYPES = [
        ('new_article', 'New Article'),
        ('new_comment', 'New Comment'),
        ('new_like', 'New Like'),
        ('new_subscriber', 'New Subscriber'),
        ('article_approved', 'Article Approved'),
        ('article_rejected', 'Article Rejected'),
    ]

    recipient = ForeignKey('accounts.Profile', on_delete=CASCADE, related_name='notifications')
    notification_type = CharField(max_length=20, choices=TYPES)

    # Generic relation to any model
    content_type = ForeignKey(ContentType, on_delete=CASCADE)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    message = TextField()
    read = BooleanField(default=False)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            Index(fields=['recipient', 'read', '-created']),
        ]

    def __str__(self):
        return f"{self.notification_type} for {self.recipient}"


# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from content.models import Article
from engagement.models import Comment, Like
from notifications.models import Notification

@receiver(post_save, sender=Comment)
def notify_article_author_of_comment(sender, instance, created, **kwargs):
    if created and instance.author != instance.article.author:
        Notification.objects.create(
            recipient=instance.article.author,
            notification_type='new_comment',
            content_object=instance,
            message=f"{instance.author.full_name} commented on your article '{instance.article.title}'"
        )

@receiver(post_save, sender=Like)
def notify_article_author_of_like(sender, instance, created, **kwargs):
    if created and instance.author != instance.article.author:
        Notification.objects.create(
            recipient=instance.article.author,
            notification_type='new_like',
            content_object=instance,
            message=f"{instance.author.full_name} liked your article '{instance.article.title}'"
        )
```

**API endpoints** for notifications list, mark as read, mark all as read.

---

### 3.4 Celery Async Tasks

#### 🔴 Task 3.4.1: Configure Celery
**Time**: 6 hours
**Energy**: High
**Focus**: Learning async processing

**Create**: `blog_platform/celery.py`
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_platform.settings')

app = Celery('blog_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**Update**: `blog_platform/__init__.py`
```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

**Settings**:
```python
# settings.py
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

**Create tasks**:
```python
# notifications/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_notification_email(recipient_email, subject, message):
    send_mail(
        subject=subject,
        message=message,
        from_email='noreply@yourdomain.com',
        recipient_list=[recipient_email],
        fail_silently=False,
    )

@shared_task
def send_daily_digest():
    """Send daily email digest to subscribers"""
    # Implementation
    pass
```

**Update docker-compose.yml** to add Celery worker:
```yaml
celery:
  build: .
  command: celery -A blog_platform worker -l info
  depends_on:
    - redis
    - postgres
  env_file:
    - .env
```

---

### 3.5 Analytics Dashboard

#### 🔴 Task 3.5.1: Create Analytics Models
**Time**: 8 hours
**Energy**: High
**Focus**: Data aggregation

Track article views, engagement metrics, subscriber growth.

**Create**: `analytics` app with models for tracking.

---

### 3.6 OAuth2 Authentication

#### 🔴 Task 3.6.1: Add Google OAuth
**Time**: 6 hours
**Energy**: High
**Focus**: Third-party integration

Use `django-allauth` for social authentication.

---

### 3.7 Performance Optimizations

#### 🟡 Task 3.7.1: Database Query Optimization
**Time**: 4 hours
**Energy**: Medium

Add `select_related`, `prefetch_related`, optimize N+1 queries.

#### 🟡 Task 3.7.2: Implement Redis Caching
**Time**: 5 hours
**Energy**: Medium

Cache views, querysets, expensive operations.

---

### 3.8 Email System

#### 🟡 Task 3.8.1: Configure Email Backend
**Time**: 4 hours
**Energy**: Medium

Setup SendGrid/Mailgun, create email templates.

---

### 3.9 File Uploads

#### 🟡 Task 3.9.1: Add Featured Images
**Time**: 4 hours
**Energy**: Medium

Allow article featured images with Cloudinary processing.

---

### 3.10 Security Enhancements

#### 🟡 Task 3.10.1: Add Rate Limiting
**Time**: 3 hours
**Energy**: Medium

Implement `django-ratelimit` on API endpoints.

#### 🟢 Task 3.10.2: Add CAPTCHA
**Time**: 2 hours
**Energy**: Low

Use `django-recaptcha` on signup/comment forms.

---

## Development Workflow Optimization

### 1. Task Switching Strategy

**Energy-Based Task Selection**:

```markdown
Morning (High Energy):
- 🔴 Hard Backend Tasks (Celery, Search, Notifications)
- Complex problem solving
- Learning new concepts

Afternoon (Medium Energy):
- 🟡 Medium Frontend/Backend
- API development
- Feature implementation

Evening (Low Energy):
- 🟢 Easy Frontend Tasks
- CSS styling
- Component creation
- Documentation
```

**Weekly Planning Template**:
```markdown
Monday:
- [ ] 🔴 1 Hard Backend Task (4-6h)
- [ ] 🟢 1-2 Easy Frontend Tasks (2h)

Tuesday:
- [ ] 🟡 1-2 Medium Frontend Tasks (4-6h)

Wednesday:
- [ ] 🔴 1 Hard Backend Task (4-6h)
- [ ] 🟢 Polish/Bug fixes (2h)

Thursday:
- [ ] 🟡 1-2 Medium Backend Tasks (4-6h)

Friday:
- [ ] 🟢 Multiple Easy Tasks (catch-up)
- [ ] Testing & Documentation

Weekend (Optional):
- [ ] 🟡 Medium Frontend (Visual work is relaxing)
```

---

### 2. Git Workflow

**Branch Strategy**:
```bash
main (production)
├── dev (development)
    ├── feature/api-layer
    ├── feature/tagging-system
    ├── feature/search
    ├── frontend/homepage-redesign
    ├── frontend/article-page
    └── backend/notifications
```

**Commit Convention**:
```bash
# Feature
git commit -m "feat: add article tagging system"

# Frontend
git commit -m "style: redesign homepage hero section"

# Backend
git commit -m "backend: implement full-text search"

# Fix
git commit -m "fix: resolve article slug duplication"

# Test
git commit -m "test: add API endpoint tests"
```

**Deploy Points**:
```markdown
1. After Part 1 → Deploy to Hetzner (Week 1)
2. After Part 2 → Deploy frontend changes (Week 3-4)
3. After Part 3 → Final deployment (Week 6-8)
```

---

### 3. Development Environment Setup

**Use Docker for consistency**:
```bash
# Start development environment
docker-compose up -d

# Watch logs
docker-compose logs -f web

# Run tests
docker-compose exec web python manage.py test

# Generate mock data
docker-compose exec web python manage.py generate_mock_data
```

**Use hot reload for frontend**:
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Tailwind watcher (if using)
npm run watch

# Terminal 3: Tests (optional)
ptw # pytest-watch
```

---

### 4. Testing Strategy

**Test as you go**:
```python
# For each new feature, write tests immediately
# Example: After creating tagging API
python manage.py test content.tests.test_tags_api -v 2

# Check coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Visual coverage report
```

**Pre-commit hooks** (optional):
```bash
# .git/hooks/pre-commit
#!/bin/bash
python manage.py test --failfast
black .
flake8 .
```

---

### 5. Documentation Practices

**Update docs immediately after completing feature**:
```markdown
After implementing tagging:
1. Update API docs
2. Add usage example to README
3. Update CHANGELOG.md
4. Screenshot for portfolio
```

---

### 6. Progress Tracking

**Use GitHub Projects**:
- Column: Todo
- Column: In Progress
- Column: Testing
- Column: Done

**Weekly Review**:
```markdown
Friday Review:
- What did I complete?
- What blocked me?
- What did I learn?
- Next week priorities
```

---

### 7. Learning Resources

**For Backend Tasks**:
- Django REST Framework docs: https://www.django-rest-framework.org/
- Celery docs: https://docs.celeryproject.org/
- PostgreSQL full-text search: https://www.postgresql.org/docs/current/textsearch.html

**For Frontend Tasks**:
- Tailwind CSS: https://tailwindcss.com/docs
- CSS Grid/Flexbox: https://css-tricks.com/
- JavaScript async/await: https://javascript.info/async-await

---

### 8. Avoid Burnout

**Rules**:
1. **1 hard task per day maximum**
2. **Take breaks every 90 minutes**
3. **Don't work on weekends unless you want to**
4. **Switch to easy tasks when tired**
5. **Celebrate small wins** (completed feature → commit → screenshot)

**Pomodoro Technique**:
```
25 min work → 5 min break → repeat 4x → 30 min break
```

---

## Testing Strategy

### Unit Tests
- Models: All methods, properties
- Views: Permissions, responses
- API: Endpoints, serialization
- Forms: Validation

### Integration Tests
- User flows (signup → create article → comment)
- API workflows
- Search functionality

### Performance Tests
- Load testing with locust
- Query optimization

**Goal**: 80%+ coverage before deployment

---

## Quality Checklist

### Before Each Deployment

**Code Quality**:
- [ ] All tests pass
- [ ] No linting errors
- [ ] Code formatted (black)
- [ ] No security vulnerabilities (safety check)

**Functionality**:
- [ ] All features work on development
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Cross-browser tested (Chrome, Firefox, Safari)

**Performance**:
- [ ] Page load < 2s
- [ ] No N+1 queries
- [ ] Images optimized
- [ ] Static files compressed

**Documentation**:
- [ ] README updated
- [ ] API docs current
- [ ] CHANGELOG updated
- [ ] Environment variables documented

**Security**:
- [ ] Debug=False in production
- [ ] SECRET_KEY is secret
- [ ] HTTPS enabled
- [ ] CSRF protection active
- [ ] SQL injection prevented
- [ ] XSS prevented

---

## Success Metrics

**Portfolio Ready When**:
1. ✅ Live demo with realistic data
2. ✅ Professional UI/UX
3. ✅ Working API with docs
4. ✅ 80%+ test coverage
5. ✅ Sub-2s page loads
6. ✅ Mobile responsive
7. ✅ Comprehensive README
8. ✅ Clean, well-documented code

**Employer Impression**:
- Shows modern Django + DRF skills
- Demonstrates async processing (Celery)
- Good database design
- Security awareness
- API development
- Testing practices
- DevOps (Docker, deployment)
- UI/UX skills

---

## Timeline Summary

| Phase | Duration | Outcome |
|-------|----------|---------|
| **Part 1** | 1 week (20h) | Critical fixes + API + Deploy |
| **Part 2** | 2-3 weeks (40h) | Professional UI |
| **Part 3** | 3-4 weeks (55h) | Advanced features |
| **Total** | **6-8 weeks part-time** | **Portfolio-ready project** |

If working full-time (40h/week):
- **Part 1**: 3-4 days
- **Part 2**: 1 week
- **Part 3**: 1.5 weeks
- **Total**: ~3 weeks

---

## Next Steps

1. **Read through this document**
2. **Set up task board** (GitHub Projects or Trello)
3. **Start with Part 1, Task 1.1** (Fix requirements.txt)
4. **Follow the checklist**
5. **Track progress daily**
6. **Deploy after Part 1**
7. **Continue with Parts 2 & 3 flexibly**

---

## Questions?

As you work through tasks, document:
- Problems encountered
- Solutions found
- Time spent vs estimated
- Learning resources used

This helps refine estimates and processes.

**Good luck! You've got a solid foundation to build on.** 🚀
