# Architecture

## System Design

```
Browser
  │
  ├── http://localhost:4321 ──► Astro (SSR)
  │                                │
  │                                │ server-side fetch (api.ts)
  │                                ▼
  │                        http://localhost:8000
  │                           Django REST API
  │                                │
  │                      ┌─────────┴──────────┐
  │                      ▼                    ▼
  │                 PostgreSQL              Redis
  │                 (primary DB)           (cache, optional)
  │
  └── http://localhost:8000/admin/ ──► Django Admin (HTML)
```

All public page rendering happens **server-side in Astro**. Astro fetches from Django's API at request time and returns fully-rendered HTML to the browser. There are no client-side API calls for page content.

The Django admin panel remains a traditional server-rendered Django application and is separate from the Astro frontend.

---

## Data Flow — Reading an Article

```
1. Browser  GET /articles/my-article-slug
2. Astro    server: calls getArticle('my-article-slug')
3. api.ts   fetch http://localhost:8000/api/v1/articles/my-article-slug/
4. Django   ArticleViewSet.retrieve() → checks visibility/auth
5. Django   returns JSON (ArticleDetail)
6. Astro    renders [slug].astro with data → returns HTML
7. Browser  receives complete HTML page
```

---

## Backend Internal Architecture

```
backend/
├── blog_platform/      Django project (settings, urls, wsgi)
├── accounts/           User profiles and auth
│   ├── models.py       Profile (extends User)
│   ├── views.py        HTML views (login, signup, profile)
│   └── urls.py         HTML URL routes
├── content/            Core content
│   ├── models.py       Bulletin, Article, Subscription
│   ├── api_views.py    ArticleViewSet, BulletinViewSet, SubscriptionViewSet
│   ├── api_urls.py     API URL router
│   ├── serializers.py  DRF serializers
│   ├── views.py        Legacy HTML views (to be removed)
│   └── urls.py         Legacy HTML URL routes (to be removed)
├── engagement/         User interactions
│   ├── models.py       Comment, Like, ReadLater
│   ├── api_views.py    CommentViewSet, ReadLaterViewSet
│   ├── api_urls.py     API URL router
│   └── serializers.py  DRF serializers
└── core/               Shared utilities
    ├── sanitization.py bleach HTML sanitizer
    ├── cache.py        Cache TTL constants and key builders
    └── management/     Django management commands
```

---

## Frontend Internal Architecture

```
frontend/src/
├── lib/
│   └── api.ts          Typed API client (all backend calls go here)
├── layouts/
│   └── BaseLayout.astro HTML shell, imports Header + Footer
├── components/
│   ├── Header.astro    Navigation bar
│   ├── Footer.astro    Footer
│   ├── ArticleCard.astro Article summary card
│   └── Pagination.astro Page navigation
├── pages/
│   ├── index.astro             Home — latest articles + bulletins
│   ├── articles/
│   │   ├── index.astro         Article list with search + pagination
│   │   └── [slug].astro        Article detail with comments
│   └── bulletins/
│       ├── index.astro         Bulletin list with search
│       └── [slug].astro        Bulletin detail with article list
└── styles/
    └── global.css      Tailwind import + prose styles for article content
```

---

## Authentication Architecture

The API uses **JWT tokens** (access + refresh pair).

```
POST /api/v1/auth/token/          { username, password } → { access, refresh }
POST /api/v1/auth/token/refresh/  { refresh }            → { access }
```

- Access token lifetime: **1 hour**
- Refresh token lifetime: **7 days**, rotates on use
- Tokens are sent as `Authorization: Bearer <access>` header

Public endpoints (article list, article detail, bulletins) work without authentication. Writing, liking, bookmarking, and commenting require a valid access token.

The Astro frontend does not yet implement auth — login pages are a planned next step.

---

## Legacy Django HTML Views

Django still has a full set of HTML template views (`content/views.py`, `accounts/views.py`, `engagement/views.py`) from the pre-API version of the project. These are served on `http://localhost:8000` but are not used by the Astro frontend.

**These are candidates for removal** once the Astro frontend covers the same functionality. The admin panel (`/admin/`) should be kept.

---

## CORS Configuration

Django allows cross-origin requests from:
- `http://localhost:4321` (Astro dev server)
- `http://127.0.0.1:4321`
- Any URL set in `FRONTEND_URL` env var (for production)
