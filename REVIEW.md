# Blog Platform — Senior Code Review

**Date:** 2026-09-04
**Scope:** Backend (`settings`, models, all views, API layer, serializers, mixins, sanitization,
Docker/deploy), Astro frontend, project structure and dependencies.
**Reviewer perspective:** senior developer, pre-merge review.

---

## TL;DR

There is a real project here with good bones: clean app separation
(`accounts` / `content` / `engagement` / `core`), a sensible domain model, a genuinely
well-built REST API, and a broad automated test suite. The author clearly knows Django.

The problems are mostly **accumulated cruft from unfinished migrations** (editors, storage
backends, config libraries), a **split-brain frontend** (Django templates *and* an Astro SPA
maintained in parallel), a **dead caching layer**, and a handful of **access-control gaps on
the server-rendered side** that the API layer does not share.

**Merge recommendation:** block on the Critical section; file the rest as tracked tech debt.

---

## Critical — Security / Access Control

### 1. Template views have no authorization

The API does role-based filtering correctly (`ArticleViewSet.get_queryset`). The Django
template views do not:

| View | Problem |
|------|---------|
| `ArticleDetailView` (`/article/<pk>/`) | Bare `DetailView`, no queryset filter. **Any anonymous visitor can read any draft, private, or rejected article by guessing the ID.** |
| `ArticleListView` | Docstring: *"Lists all articles from database without status filtering."* |
| `BulletinUpdateView` | No `LoginRequiredMixin`, no ownership check. Docstring: *"authorization should be checked in template."* |
| `ProfileUpdateView` | No auth mixin. Anyone can `POST` to `/accounts/<username>/edit/` and edit another user's profile. |
| `BulletinDashboardView` | No auth mixin; exposes another writer's drafts. |

Template-level hiding is not access control. These need `LoginRequiredMixin` plus
object-level ownership tests — the same pattern already implemented for the API in
`perform_update` / `perform_destroy`.

### 2. Comments API leaks across visibility boundaries

`CommentViewSet.get_queryset` returns `Comment.objects.all()`. Any authenticated user can
read comments on private or draft articles via `?article=<id>`. The queryset must be scoped
to articles the requesting user is allowed to see (reuse the article visibility logic).

### 3. JWT has no revocation path

```python
SIMPLE_JWT = {
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,   # and no blacklist app installed
}
```

- A stolen refresh token is valid for 7 days with no way to invalidate it.
- Rotated-away refresh tokens remain valid.
- There is no API logout.

Add `rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS`, set
`BLACKLIST_AFTER_ROTATION: True`, and expose a logout/blacklist endpoint.

### 4. No rate limiting on authentication

`django-ratelimit` is in `requirements.txt` but used nowhere. `/api/v1/auth/token/` is open
to unlimited brute-force attempts. Add throttling (DRF `ScopedRateThrottle` or
`django-ratelimit`) to the token endpoint and to signup.

### 5. `django-csp` is active but unconfigured

`csp.middleware.CSPMiddleware` is in `MIDDLEWARE`, but there is no `CONTENT_SECURITY_POLICY`
/ `CSP_*` configuration. The middleware is effectively a no-op. Either configure a real
policy or remove the middleware and the dependency.

### 6. HTML sanitization allowlist is too permissive

`core/sanitization.py`:

```python
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style'],   # style on every element, no CSS sanitizer
    ...
}
ALLOWED_TAGS = [..., 'div', 'span', ...]
```

The Astro frontend renders article bodies with `set:html={article.content}`, so this
allowlist is the **only** XSS barrier. Tighten it:

- Drop `style` (or add `bleach.css_sanitizer.CSSSanitizer` with a narrow property list).
- Restrict `a` / `img` to `http`, `https`, `mailto` protocols (bleach only enforces this
  for links by default).
- Force `rel="noopener noreferrer"` whenever `target="_blank"` is present.
- Reconsider bare `div` / `span`.

### 7. Contradictory cookie / CORS configuration

```python
SESSION_COOKIE_SAMESITE = 'Strict'
CORS_ALLOW_CREDENTIALS = True
```

`Strict` also breaks the normal "follow a link into the site → appear logged out" flow.
`Lax` is almost certainly the intended value.

### 8. Default admin credentials on every deploy

The container `CMD` runs `create_superuser_from_env` on every boot, and `.env.example`
ships `SUPERUSER_PASSWORD=changeme`. It is very easy to deploy a live site with a default
admin account. At minimum, fail loudly if the password is unset or equals a known default.

---

## Critical — Correctness

### 9. The Redis cache layer is entirely dead code

```python
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
```

`CACHES` is hardcoded to `DummyCache` unconditionally. `REDIS_URL` is read, printed to
stdout, and **never used to configure a backend**. Consequences:

- Every `cache.get()` returns `None`; every `cache.set()` is a no-op.
- `@method_decorator(cache_page(...))` on `HomePageView` does nothing (and adds overhead).
- All ~30 TTL constants in `core/cache.py` and the homepage / bulletin caching are inert.
- README's *"Redis caching for performance"* is false.

Decision required: wire up `django-redis` properly, or delete the entire caching layer.
As-is it is misleading overhead.

### 10. `Article.save()` overwrites `published` on every edit

```python
if self.status == 'published':
    self.published = timezone.now()
```

Every save of an already-published article resets its publish date. Fix:

```python
if self.status == 'published' and self.published is None:
    self.published = timezone.now()
```

### 11. Slug collision → `IntegrityError` (500)

`unique_together = ('bulletin', 'title')` permits the same title in two different bulletins,
but `slug = slugify(self.title)` with `unique=True` and no dedupe loop. The second article
with a colliding slug raises `IntegrityError` on create. Append a counter / short hash, or
scope the slug per bulletin.

### 12. Two `Profile` methods are broken

```python
def get_articles_liked_count(self):
    return Like.objects.filter(user=self.user).count()      # Like has no `user` field

def get_comments_posted_count(self):
    return Comment.objects.filter(author=self.user).count() # Comment.author is a Profile FK
```

`Like` fields are `author` (→ `Profile`), `article`, `created`. Both methods raise
`FieldError` whenever called. Not covered by tests. Fix the lookups (`author=self`) or
remove the methods.

### 13. N+1 queries throughout the API list serializers

`likes_count`, `comments_count`, `subscribers_count`, `articles_count` are all
`SerializerMethodField`s calling `.count()` per row. A 20-item article list issues 60+
queries. Use `.annotate(Count(...))` in the viewset queryset.

Also: `ArticleViewSet` does `select_related('bulletin__owner')` but the author serializer
accesses `obj.author.user.username` and `obj.author.avatar_url` → `bulletin__owner__user`
is not selected, adding another query per row.

### 14. Missing-relation crashes

- `ArticleViewSet.perform_create`: a writer with no `bulletin` triggers
  `RelatedObjectDoesNotExist` (500).
- Every `self.request.user.profile` access assumes the `post_save` signal always fired. A
  superuser created via `createsuperuser`, or any user created before the signal existed,
  has no `Profile` → 500. Add a safety net (`get_or_create`, or a data migration + a
  management command to backfill).

### 15. `BulletinDetailView` caches a lazy `QuerySet`

`cache.set(cache_key, articles, ...)` where `articles` is an unevaluated `QuerySet`.
Harmless today only because the cache is `DummyCache`; a latent bug if Redis is ever wired
up. Cache a concrete `list(...)` or cache the rendered fragment.

### 16. `ArticleSearchView` runs its query twice

`get_context_data` calls `self.get_queryset().count()` after `ListView` has already
evaluated the same queryset for pagination. Cache the queryset on `self` or use the
paginator's `count`.

---

## High — Architecture / Project Health

### 17. Two parallel frontends

A complete Django template site (~25 templates, ~15 template views, forms, URL routes)
*and* a separate Astro SPA against the same API. Recent commits ("Create Astro frontend",
"Remove frontend components", "Build base layout") indicate an in-progress migration, but
the template views remain fully wired in `urls.py`, untouched — and they are the insecure
half (see Critical §1).

Pick one. If Astro is the target, remove the template views / URLs / forms now rather than
maintaining (and securing) both.

### 18. `requirements.txt` is an unfiltered `pip freeze` dump

Starts with a UTF-8 BOM. Contains multiple redundant stacks:

| Purpose | Packages present | Needed |
|---------|-----------------|--------|
| Cloudinary/media | `cloudinary`, `django-cloudinary-storage`, `dj3-cloudinary-storage`, plus `boto3` + `django-storages` + `s3transfer` | one |
| Rich text editor | `django-ckeditor`, `django-ckeditor-5`, `martor` (+ `Markdown`) | one |
| Config / env | `python-dotenv`, `python-decouple`, `django-environ` | one (settings uses none — raw `os.getenv`) |
| Async tasks | `celery`, `django_celery_results`, `amqp`, `kombu`, `billiard`, `vine` | **zero — no Celery app, no tasks** |
| Browser tests | `selenium`, `trio`, `trio-websocket`, `outcome`, `sortedcontainers` | dev-only, not prod |

Also installed-but-unused: `django-ratelimit`, `crispy-tailwind` (+ `martor`) alongside
direct `bleach` use.

Action: curate a real dependency list (or `pyproject.toml` + lockfile), split dev vs prod.
This will materially cut image size and attack surface.

### 19. `print()` in `settings.py`

Runs on every management command, including `migrate` / `collectstatic` in production. One
line prints `REDIS_URL[:30]` — which leaks credentials when the URL is
`redis://user:pass@host`. Replace with `logging` or remove.

### 20. Import-time `'test' in sys.argv` branching

Present in both `settings.py` and `accounts/models.py`. Fragile — breaks under `pytest`,
under CI runners, and whenever the invocation path contains "test". Conditionally setting
`MediaCloudinaryStorage = None` inside a model module means migrations bake different
storage depending on how they were generated. Use a dedicated `settings/test.py` (or
`DJANGO_SETTINGS_MODULE`) instead.

### 21. `entrypoint.sh` is dead and wrong

```sh
#!/bin/zsh
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

`zsh` is not in `python:3.11-slim`; `makemigrations` must never run at container start
(migrations are committed artifacts); and the file is unused because the `Dockerfile`
inlines its own `CMD`. Delete it.

### 22. No CI; `.coverage` committed

20 test files, no `.github/workflows`. Tests only run when someone remembers to run them
locally. The binary `.coverage` file is committed to the repo — add it to `.gitignore` and
add a CI workflow that runs the suite (and ideally reports coverage).

### 23. Documentation rot

`README.md` links five documents that do not exist: `DEVELOPMENT.md`, `DEPLOYMENT.md`,
`DEPLOY_CHECKLIST.md`, `CLAUDE.md`, `NOTES.md`. It says "Railway" in one section and
"Hetzner + Coolify" in another. The actual docs live in `docs/analysis/*` and look
auto-generated. Consolidate to one accurate set.

---

## Medium

- **Deprecated storage settings.** `STATICFILES_STORAGE` / `DEFAULT_FILE_STORAGE` are
  superseded by the `STORAGES` dict in Django 4.2+. Works in 5.2 with deprecation warnings.
- **"Popular bulletins" is not popular.** `HomePageView` caches
  `list(Bulletin.objects.all()[:3])` — no ordering by subscriber count. "Recent writers"
  is likewise unordered.
- **Leftover editor import.** `content/models.py` imports `RichTextField` from
  `ckeditor.fields` (unused) alongside `CKEditor5Field`.
- **Hardcoded Slovak strings** in `messages.*` calls, with `LANGUAGE_CODE = 'en-us'` and
  English templates. Choose one language, or adopt `gettext` + locale files.
- **`Article.content` is `null=True, blank=True`** at the DB level but the forms treat
  empty content as invalid — inconsistent contract.
- **`PromoteReaderToAdminView`** has a muddled guard:
  `if request.user.username != username and not request.user.is_superuser` — the second
  clause is always false at that point (non-superusers already returned). Functionally OK,
  logically confusing.
- **`unique_together`** is soft-deprecated in favor of `Meta.constraints` /
  `UniqueConstraint`.
- **Import style.** `from django.db.models import Model, CASCADE, CharField, ...` instead
  of `models.CharField`. Unconventional, hurts readability, and is why the dead
  `RichTextField` import went unnoticed.
- **`docker-compose.yml`** hardcodes `DEBUG=True` and `postgres/postgres`, and the frontend
  service runs `npm install -g pnpm && pnpm install` on every `up`. Acceptable for local
  dev, but there is no production compose file — the `Dockerfile` is the only prod artifact.
- **Detail serializer exposes `evaluation`** (moderation state) to any reader. Low impact
  but unnecessary.

---

## What's genuinely good

- **API `get_queryset` role logic** (anon / reader / writer / admin) is correct and
  cleanly written — the hardest part, done well.
- **Real, broad test coverage** across every app: models, views, forms, API, admin,
  integration, search, Selenium GUI. More discipline than most projects this size.
- **Centralized sanitization applied at the model layer** (defense in depth) — right
  instinct, just needs a tighter allowlist.
- **Thoughtful composite DB indexes** matching the actual query patterns
  (`status/visibility/evaluation`, `bulletin/status`, `evaluation/created`).
- **API tooling done properly:** drf-spectacular / OpenAPI, JWT, filtering, search,
  ordering, pagination all wired correctly.
- **Security headers** — HSTS, `nosniff`, `X-Frame-Options: DENY`, secure cookies, SSL
  redirect, proxy SSL header — all configured and correctly gated on `DEBUG`.
- **Complete, well-commented `.env.example`;** real secrets are gitignored.
- **Deployment basics considered:** health check endpoint, gunicorn with sane worker
  config, Faker-based mock-data command for onboarding.
- **Unusually thorough view docstrings** (even where they candidly document the gaps).

---

## Suggested priority order

**This week (blockers):**
1. Add `LoginRequiredMixin` + object-level ownership checks to every template view that
   mutates or exposes data — or delete the template frontend entirely.
2. Scope `CommentViewSet.get_queryset` to visible articles.
3. Decide Redis in or out; fix or delete the cache layer accordingly.
4. Fix `Article.save()` published-date bug and the slug-collision crash.
5. Add throttling to the JWT token endpoint; add the token blacklist app.

**This month (tech debt):**
6. Prune `requirements.txt` to what is actually imported; split dev / prod.
7. Add a CI workflow running the existing test suite; gitignore `.coverage`.
8. Remove one of the two frontends.
9. Fix the N+1s in the API serializers with `annotate`.
10. Remove `print()` from settings; move test config out of `sys.argv` branching.
11. Reconcile the README with reality; delete `entrypoint.sh`.

**Backlog:**
12. Configure `django-csp` or drop it.
13. Fix / remove the two broken `Profile` methods.
14. Migrate to the `STORAGES` setting; `unique_together` → `UniqueConstraint`.
15. Decide on a single UI language.
