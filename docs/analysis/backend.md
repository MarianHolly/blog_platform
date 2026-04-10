# Backend

Django 5.2 REST API. Lives in `backend/`.

---

## Django Apps

### `accounts`
User authentication and profile management.

- **Model:** `Profile` — extends Django's `User` via `OneToOneField`. Holds role, bio, avatar.
- **Roles:** `reader` (default), `writer`, `admin`
- **Signal:** Profile is auto-created on User creation via `post_save` signal (`signals.py`)
- **Views:** Legacy HTML views for login, signup, profile pages (not used by Astro)
- **Management command:** `create_superuser_from_env` — creates admin from env vars on deploy

### `content`
Core content models and API.

- **Models:** `Bulletin`, `Article`, `Subscription`
- **API ViewSets:** `ArticleViewSet`, `BulletinViewSet`, `SubscriptionViewSet`
- **Key behavior:**
  - Articles are sanitized by `bleach` on every save
  - Slug is auto-generated from title on first save
  - `published` timestamp is set automatically when status changes to `published`
  - Article visibility enforced at queryset level in `get_queryset()`

### `engagement`
User interaction models.

- **Models:** `Comment`, `Like`, `ReadLater`
- **API ViewSets:** `CommentViewSet`, `ReadLaterViewSet`
- **Like/bookmark** use toggle pattern — POST creates if not exists, deletes if exists

### `core`
Shared utilities, no models.

- `sanitization.py` — `bleach`-based HTML sanitizer with allowed tag/attribute allowlist
- `cache.py` — cache TTL constants and cache key builder functions
- `management/` — management commands

---

## Permissions

| Action | Anonymous | Reader | Writer | Admin |
|---|---|---|---|---|
| List/read public articles | ✓ | ✓ | ✓ | ✓ |
| Read subscribed private articles | ✗ | ✓ | ✗ | ✓ |
| Create article | ✗ | ✗ | ✓ (own bulletin) | ✗ |
| Edit/delete article | ✗ | ✗ | ✓ (own only) | ✗ |
| Like / bookmark | ✗ | ✓ | ✓ | ✓ |
| Comment | ✗ | ✓ | ✓ | ✓ |
| Subscribe to bulletin | ✗ | ✓ | ✗ | ✓ |
| Admin panel | ✗ | ✗ | ✗ | ✓ |

Permissions are enforced via DRF permission classes and `get_queryset()` filtering — not just view-level checks.

---

## DRF Configuration

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',   # browsable API
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ],
}
```

JWT tokens: access 1 hour, refresh 7 days with rotation.

---

## Content Sanitization

All article content passes through `core.sanitization.sanitize_article_content()` on every `Article.save()`.

**Allowed HTML tags:** `p, br, strong, em, u, ol, ul, li, h1-h6, a, img, blockquote, code, pre, hr, table, thead, tbody, tr, th, td, div, span, figure, figcaption`

**Allowed attributes:**
- `a`: `href, title, target, rel`
- `img`: `src, alt, title, width, height`
- `*`: `class, style`
- `table/td/th`: `border, cellpadding, cellspacing, colspan, rowspan`

---

## Caching

Redis is **optional**. If `REDIS_URL` is not set, the app falls back to `DummyCache` and database sessions — all functionality works, just without caching.

Cache TTL constants are defined in `core/cache.py` for consistency. Current usage of caching in views is minimal (cache infrastructure is in place, not yet applied to API views).

---

## Celery

Celery is installed and configured in `requirements.txt` (`celery`, `django_celery_results`, `kombu`, `billiard`, `amqp`). No tasks have been implemented yet. Redis would serve as the broker when tasks are added.

---

## Legacy HTML Views

`content/views.py`, `content/urls.py`, `accounts/views.py`, `accounts/urls.py`, `engagement/views.py`, `engagement/urls.py` — all still present and mounted in `blog_platform/urls.py`.

These serve the old Django-template-based frontend and are **not used by the Astro frontend**. They are candidates for removal once Astro covers the same functionality. The templates directory (`backend/templates/`) can be removed at the same time.

---

## Management Commands

| Command | Description |
|---|---|
| `python manage.py generate_mock_data` | Creates users, bulletins, articles, subscriptions, likes, comments with Faker |
| `python manage.py generate_mock_data --users 50 --articles 100` | Custom counts |
| `python manage.py generate_mock_data --clear` | Clear and regenerate |
| `python manage.py create_superuser_from_env` | Creates admin from env vars |
