# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Blog Platform** is a Django-based content management system with role-based permissions (Reader, Writer, Admin). Writers publish articles through personal "Bulletins," readers subscribe and engage through likes/comments/bookmarks, and admins moderate content through an evaluation workflow.

Key Stack:
- **Backend**: Django 5.2 with PostgreSQL
- **Frontend**: Django templates + Tailwind CSS + CKEditor5
- **Storage**: Cloudinary for media (images/uploads)
- **Caching**: Redis (with database session fallback)
- **Task Queue**: Celery (configured but minimal usage currently)

## Essential Commands

### Local Development Setup
```bash
# Create virtual environment and activate
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from environment variables (see below)
```

### Running the Server
```bash
# Development server
python manage.py runserver

# Production-like (gunicorn)
gunicorn blog_platform.wsgi:application
```

### Database Operations
```bash
# Create/apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (interactive)
python manage.py createsuperuser

# Database shell
python manage.py dbshell
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test content
python manage.py test engagement

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # generates htmlcov/index.html

# Run specific test file or class
python manage.py test content.tests.test_models
python manage.py test content.tests.test_models.ArticleModelTest
```

### Static Files & Compilation
```bash
# Collect static files for production
python manage.py collectstatic --noinput

# Clear static file cache
python manage.py collectstatic --clear --noinput
```

### Useful Django Management
```bash
# Drop into Python shell with Django context
python manage.py shell

# Check for Django issues
python manage.py check

# List all URLs
python manage.py show_urls
```

## Environment Configuration

Create a `.env` file in the project root with:
```
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True  # False in production
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/blog_platform
# OR individual settings:
# DB_NAME=blog_platform
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Cloudinary (media storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Superuser creation (build.sh uses these)
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@blogplatform.com
SUPERUSER_PASSWORD=admin123
```

## High-Level Architecture

### Data Model Relationships

```
User (Django)
  ↓ OneToOne (cascade)
Profile [role: reader|writer|admin, avatar, biography]
  ↓ OneToOne (if writer, cascade)
Bulletin [title, slug, description]
  ↓ ForeignKey (cascade)
Article [title, content, status: draft|published, visibility: public|private, evaluation: pending|under_review|approved|rejected]
  ├─→ Comments (1:many)
  ├─→ Likes (1:many)
  └─→ ReadLater (1:many)

Subscription [ForeignKey(Profile), ForeignKey(Bulletin)] - Links readers to writer's bulletins
```

### App Structure

**accounts/** - User management and authentication
- **models.py**: Profile extends User with role field (reader/writer/admin)
- **views.py**: SignUp, Login, ProfileDetail, PromoteToWriter, PromoteToAdmin
- **mixins.py**: ReaderRequiredMixin, WriterRequiredMixin, AdministratorRequiredMixin
- **forms.py**: SignUpForm with custom validation
- **urls.py**: Authentication and profile URLs

**content/** - Articles, bulletins, and content management
- **models.py**: Article, Bulletin, Subscription with HTML sanitization on save
- **views.py**: ArticleCRUD, ArticleDetail, BulletinDetail, ArticleSearch, ArticleEvaluation, Visibility/Subscription toggles
- **mixins.py**: ArticleOwnerMixin (ensures writer can only edit own bulletin's articles)
- **forms.py**: ArticleForm, ArticleEvaluationForm
- **urls.py**: Content discovery and management URLs
- **tests/**: Comprehensive tests for models, forms, search, GUI

**engagement/** - Likes, comments, bookmarks
- **models.py**: Like, Comment, ReadLater with self-engagement prevention (views enforce it)
- **views.py**: LikeToggleView, ReadLaterToggleView
- **forms.py**: CommentModelForm
- **urls.py**: Engagement toggle URLs
- **tests/**: Model and form validation tests

**blog_platform/** - Django project configuration
- **settings.py**: Database (PostgreSQL), Redis cache, Cloudinary storage, CKEditor5 config, Security headers
- **urls.py**: Main URL routing to apps
- **ckeditor_config.py**: CKEditor5 toolbar and allowed tags
- **wsgi.py**: WSGI application entry point
- **asgi.py**: ASGI application entry point (Celery tasks, if used)

### Permission & Access Control Patterns

**Role-Based Mixins** (`accounts/mixins.py`):
```python
ReaderRequiredMixin            # Allows readers (everyone except if checking is_writer)
WriterRequiredMixin            # Allows writers only
AdministratorRequiredMixin     # Allows admins only
WriterOrSuperAdminRequiredMixin # Superuser OR writer role
```

**Content Ownership** (`content/mixins.py`):
```python
ArticleOwnerMixin  # Verifies article.bulletin == user's bulletin (prevents cross-bulletin editing)
```

**Self-Engagement Prevention** (enforced in views):
- Users cannot like their own articles (LikeToggleView)
- Users cannot bookmark own articles (ReadLaterToggleView)
- Subscriptions prevent self-subscription (SubscriptionToggleView)

### Caching Strategy
- **Homepage** (1 min): Expensive aggregation query
- **Bulletin articles** (10 min): Published content is stable
- **Fallback**: Database sessions if Redis unavailable
- **Note**: Some caching logic is incomplete (cache_page decorator ignored in certain views)

### Content Sanitization
- **Method**: HTML sanitization on Article.save() using bleach library
- **Whitelist**: p, br, strong, em, u, ol, ul, li, h1-h3 tags only
- **Purpose**: Prevent XSS attacks from rich text editor input
- **Location**: Article.save() method in content/models.py

### Article Lifecycle
1. **Draft** - Writer creates article (not searchable, private by default)
2. **Published** - Writer marks ready; admin sets to under_review
3. **Under Review** - Admin evaluates for safety/verification
4. **Approved/Rejected** - Admin decision; if rejected, article hides and writer warned

### Key Architectural Decisions

1. **Bulletin as Publishing Authority**: Each writer has exactly one Bulletin. Writers subscribe to create articles; bulletins contain multiple articles. Readers subscribe to bulletins, not individual articles. This separates publishing authority and content organization.

2. **OneToOne Profile Extension**: Avoids Django's multiple inheritance User model issues. All custom user data lives in Profile with cascade delete to User.

3. **Role Isolation**: Three distinct roles (reader/writer/admin) are mutually exclusive. Cannot be writer AND admin simultaneously. Enforced at profile creation/update.

4. **ArticleOwnerMixin Pattern**: Writers can only edit articles in their own bulletin, even if superuser. This prevents accidental cross-bulletin content edits.

5. **Engagement Model**: One comment per user per article (updatable), simple Like/ReadLater toggles with timestamps. Self-engagement prevented at view level.

6. **Content Evaluation Workflow**: Separate from publication workflow. Articles are published (draft/published status) AND evaluated (pending/under_review/approved/rejected). Allows admin moderation without blocking publication.

## Common Development Tasks

### Adding a New Field to a Model
1. Add field to model in respective `models.py`
2. Run `python manage.py makemigrations app_name`
3. Review generated migration file
4. Run `python manage.py migrate`
5. Update forms/templates if user-facing

### Creating a New View
1. Add view class to `views.py` (inherit from appropriate mixins)
2. Create template in `templates/app_name/` (naming convention: `model_action.html`)
3. Add URL pattern to `urls.py`
4. Add tests to `tests/` directory
5. Update navigation templates if needed

### Adding Tests
- Place in `app_name/tests/` directory
- Use Django's TestCase for database tests
- Import from `django.test import TestCase, Client`
- Models: Test methods, properties, unique constraints
- Forms: Test validation and save behavior
- Views: Test permissions, redirects, context data

### Article Content Validation
- CKEditor5 is configured in `blog_platform/ckeditor_config.py`
- Content auto-sanitizes on Article.save() via bleach
- Only safe HTML tags are preserved (see sanitization section above)
- Rich text toolbar configured in ckeditor_config.py

## Testing Notes

- Tests use Django's TestCase class (transaction rollback between tests)
- Uses Selenium for GUI tests (`content/tests/test_gui.py`)
- Coverage reports available via coverage tool
- `.coverage` file tracks test coverage data

## Debugging Tips

1. **Django Debug Toolbar**: Not installed; add `django-debug-toolbar` if needed for profiling
2. **Logging**: Check `settings.py` for logging configuration (different dev/prod)
3. **Shell Access**: `python manage.py shell` to query models and test code
4. **Print Debugging**: Check Django development server console output
5. **Redis Issues**: Platform falls back to database sessions if Redis unavailable (see `CACHES` in settings.py)

## Deployment Notes

- **Static Files**: Uses WhiteNoise for static file serving (no separate web server needed)
- **Media Files**: Cloudinary handles all user uploads
- **Database**: PostgreSQL in production (configured via DATABASE_URL)
- **Security**: CSRF trusted origins set for Render deployment; HSTS enabled in production
- **Build Process**: `build.sh` handles migrations, static collection, superuser creation
- **Environment**: All secrets managed via environment variables (no .env in production)

## Key Files to Know

| File | Purpose |
|------|---------|
| `blog_platform/settings.py` | Django configuration (DB, cache, security, apps) |
| `blog_platform/urls.py` | Main URL routing |
| `blog_platform/ckeditor_config.py` | Rich text editor toolbar and allowed tags |
| `accounts/models.py` | Profile model with role system |
| `accounts/mixins.py` | Role-based permission mixins |
| `content/models.py` | Article, Bulletin, Subscription with sanitization |
| `content/mixins.py` | ArticleOwnerMixin for bulletin isolation |
| `content/views.py` | Main content views (CRUD, search, evaluation) |
| `engagement/models.py` | Like, Comment, ReadLater models |
| `requirements.txt` | All Python dependencies |
| `build.sh` | Production build script |
| `Dockerfile` | Container image definition |
