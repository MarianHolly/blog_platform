# Development Guide - Blog Platform

Complete guide for setting up and developing the Blog Platform locally.

---

## Prerequisites

- **Python 3.10+** (check with `python --version`)
- **PostgreSQL 12+** (or SQLite for quick testing)
- **Redis** (optional, for caching)
- **Git**

---

## Local Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/blog_platform.git
cd blog_platform
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create `.env` file in project root:
```bash
# Django
SECRET_KEY=django-insecure-dev-key-for-local-testing-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.local

# Database (PostgreSQL recommended, SQLite works for testing)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/blog_platform

# Or individual settings:
# DB_NAME=blog_platform
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Cloudinary (for image uploads)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Superuser
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=admin123
```

### 5. Database Setup

#### Option A: PostgreSQL (Recommended)
```bash
# Create database (in psql)
CREATE DATABASE blog_platform;
CREATE USER blog_user WITH PASSWORD 'password';
ALTER ROLE blog_user SET client_encoding TO 'utf8';
ALTER ROLE blog_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE blog_platform TO blog_user;
```

#### Option B: SQLite (Quick Testing)
No additional setup needed; Django uses SQLite by default.

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 8. Load Sample Data (Optional)
Create a management command to populate test data:
```bash
python manage.py populate_sample_data
```

Or use Django shell:
```bash
python manage.py shell

from django.contrib.auth.models import User
from accounts.models import Profile
from content.models import Bulletin, Article

# Create reader
user = User.objects.create_user(username='reader1', password='test123')
Profile.objects.create(user=user, role='reader')

# Create writer with bulletin
writer = User.objects.create_user(username='writer1', password='test123')
profile = Profile.objects.create(user=writer, role='writer')
bulletin = Bulletin.objects.create(profile=profile, title="My Bulletin", slug="my-bulletin")
article = Article.objects.create(bulletin=bulletin, title="First Article", content="<p>Hello</p>", status='published', evaluation='approved')

exit()
```

---

## Running the Development Server

### Start Server
```bash
python manage.py runserver
```

Open browser: `http://localhost:8000`

### Common Issues
- **Port already in use**: `python manage.py runserver 8001`
- **Database error**: Ensure PostgreSQL is running and `DATABASE_URL` is correct
- **Static files not loading**: Run `python manage.py collectstatic`

---

## Project Structure

```
blog_platform/
├── blog_platform/          # Main Django project settings
│   ├── settings.py        # Django configuration
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI entry point
│   ├── asgi.py            # ASGI entry point
│   └── ckeditor_config.py # Rich text editor config
│
├── accounts/              # User management & authentication
│   ├── models.py          # Profile model with role system
│   ├── views.py           # Auth views (signup, login, profile)
│   ├── forms.py           # User forms
│   ├── mixins.py          # Role-based permission mixins
│   ├── urls.py            # Auth URLs
│   ├── tests/             # Account tests
│   └── management/
│       └── commands/      # Custom management commands
│
├── content/               # Articles & bulletins
│   ├── models.py          # Article, Bulletin, Subscription
│   ├── views.py           # Content views (CRUD, search, moderation)
│   ├── forms.py           # Article and evaluation forms
│   ├── mixins.py          # ArticleOwnerMixin
│   ├── urls.py            # Content URLs
│   ├── tests/             # Content tests
│   └── templatetags/      # Custom template filters
│
├── engagement/            # Likes, comments, bookmarks
│   ├── models.py          # Like, Comment, ReadLater
│   ├── views.py           # Engagement toggle views
│   ├── forms.py           # Comment form
│   ├── urls.py            # Engagement URLs
│   └── tests/             # Engagement tests
│
├── core/                  # Shared utilities
│   ├── constants.py       # Centralized role/status constants
│   ├── cache.py           # Cache utility functions
│   └── sanitization.py    # HTML content sanitization
│
├── templates/             # Django templates
│   ├── base.html          # Base template
│   ├── header.html        # Navigation header
│   ├── footer.html        # Footer
│   ├── content/           # Content templates
│   ├── accounts/          # Account templates
│   ├── engagement/        # Engagement templates
│   └── admin/             # Admin customization
│
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   │   ├── style.css      # Global styles
│   │   └── admin_custom.css # Admin theming
│   └── js/
│
├── media/                 # User-uploaded files (local dev only)
│
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
├── Procfile               # Deployment process definition
├── Dockerfile             # Container image
├── .env                   # Environment variables (local only)
└── README.md              # Project overview
```

---

## Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
python manage.py test accounts
python manage.py test content
python manage.py test engagement
```

### Run Specific Test Class
```bash
python manage.py test accounts.tests.test_models.ProfileModelTest
```

### Run with Coverage
```bash
# Install coverage if needed
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

### Testing Guidelines
- Place tests in `app_name/tests/` directory
- Use Django's `TestCase` for database tests
- Use `Client()` for view testing
- Mock external services (Cloudinary, Redis)

Example test:
```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import Profile

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test123')
        self.profile = Profile.objects.create(user=self.user, role='reader')

    def test_profile_role(self):
        self.assertEqual(self.profile.role, 'reader')

    def test_profile_creation_on_user_creation(self):
        # Test signal that auto-creates profile
        new_user = User.objects.create_user(username='new', password='test123')
        self.assertTrue(hasattr(new_user, 'profile'))
```

---

## Key Development Tasks

### Adding a New Field to a Model
1. Edit model in `app_name/models.py`
2. Create migration: `python manage.py makemigrations app_name`
3. Review generated migration file
4. Apply migration: `python manage.py migrate`
5. Update forms if user-facing
6. Update templates if needed

### Creating a New View
1. Add view class to `app_name/views.py`
2. Inherit from appropriate mixins (WriterRequiredMixin, etc.)
3. Create template in `templates/app_name/`
4. Add URL pattern to `app_name/urls.py`
5. Write tests in `app_name/tests/`
6. Update navigation if needed

### Working with Permissions
```python
# In views.py
from accounts.mixins import WriterRequiredMixin, AdministratorRequiredMixin

class CreateArticleView(WriterRequiredMixin, CreateView):
    """Only writers can create articles"""
    model = Article
    form_class = ArticleForm
    template_name = 'content/article_form.html'

class ArticleEvaluationView(AdministratorRequiredMixin, UpdateView):
    """Only admins can evaluate articles"""
    model = Article
    form_class = ArticleEvaluationForm
```

### Content Sanitization
All user-provided HTML is automatically sanitized:
```python
from core.sanitization import sanitize_html

# Automatic on save
article.content = '<p>User content</p><script>alert("xss")</script>'
article.save()  # Script tag is removed

# Manual sanitization
clean_content = sanitize_html(untrusted_html)
```

---

## Using the Admin Panel

### Access Admin
```
http://localhost:8000/admin
```

### Admin Tasks
- **Create/edit users**: Users → Add user
- **Promote to writer**: Accounts → Profiles → Select user → change role to 'writer'
- **Create bulletin**: Bulletins → Add bulletin
- **Review articles**: Articles → Evaluate status

### Admin Dashboard
```
http://localhost:8000/accounts/admin-dashboard
```
View pending article reviews and evaluation history.

---

## Database Shell

Access database directly:
```bash
python manage.py dbshell

# PostgreSQL commands
\dt                    # List tables
\d article             # Describe article table
SELECT * FROM accounts_profile;
```

---

## Django Shell

Interactive Python with Django context:
```bash
python manage.py shell

# Query examples
from accounts.models import Profile
writers = Profile.objects.filter(role='writer')
print(f"Total writers: {writers.count()}")

# Create test data
from django.contrib.auth.models import User
user = User.objects.create_user(username='testuser', password='test123')
```

---

## Troubleshooting

### "ModuleNotFoundError" on Import
```bash
# Reinstall requirements
pip install -r requirements.txt
```

### Database Connection Error
```bash
# Check PostgreSQL is running
# On Windows: services.msc → PostgreSQL → Start
# On Mac: brew services start postgresql

# Verify DATABASE_URL in .env
# Test connection: psql $DATABASE_URL
```

### Static Files Not Showing
```bash
python manage.py collectstatic --clear --noinput
```

### Redis Connection Error
```bash
# Redis is optional; falls back to database sessions
# To use Redis:
# 1. Install Redis locally
# 2. Start Redis server
# 3. Set REDIS_URL in .env
```

### Migration Conflicts
```bash
# Show migration history
python manage.py showmigrations

# Undo last migration
python manage.py migrate app_name 0001
# Then delete the conflicting migration file
# Recreate: python manage.py makemigrations
```

---

## Code Style

### Python
- Follow PEP 8 (use `black` for auto-formatting)
- Type hints where helpful
- Docstrings for functions/classes

```bash
pip install black
black .  # Auto-format
```

### HTML/CSS
- Use Tailwind CSS utility classes
- Custom colors via inline `style` attributes
- Keep templates readable with proper indentation

### Django Best Practices
- Use querysets efficiently (select_related, prefetch_related)
- Create custom managers for complex queries
- Use signals sparingly (they hide dependencies)
- Validate at form layer, not just model

---

## Git Workflow

### Feature Development
```bash
# Create feature branch
git checkout -b feature/article-search

# Make changes
git add .
git commit -m "feat: implement article search"

# Push to remote
git push origin feature/article-search

# Create pull request on GitHub
```

### Before Pushing
```bash
# Run tests
python manage.py test

# Check for issues
python manage.py check

# Review migrations
python manage.py showmigrations
```

---

## Performance Tips

### Database Queries
```python
# BAD - N+1 query problem
articles = Article.objects.all()
for article in articles:
    print(article.bulletin.title)  # Query per article

# GOOD - Single query
articles = Article.objects.select_related('bulletin')
for article in articles:
    print(article.bulletin.title)  # No extra queries
```

### Caching
```python
from core.cache import get_cache, set_cache

# Cache article detail
cache_key = f'article_{article_id}'
cached = get_cache(cache_key)
if not cached:
    article = Article.objects.get(id=article_id)
    set_cache(cache_key, article, timeout=600)  # 10 minutes
```

### Admin Optimization
Admin uses select_related/prefetch_related in list_select_related:
```python
# See accounts/admin.py and content/admin.py
class ArticleAdmin(admin.ModelAdmin):
    list_select_related = ['bulletin', 'bulletin__profile']
```

---

## Useful Commands Summary

```bash
# Server
python manage.py runserver

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# Testing
python manage.py test
coverage run --source='.' manage.py test && coverage report

# Data
python manage.py createsuperuser
python manage.py populate_sample_data
python manage.py shell

# Admin
python manage.py changepassword <username>

# Static files
python manage.py collectstatic

# Checks
python manage.py check
python manage.py show_urls
```

---

## Next Steps

After local setup:
1. Read **CLAUDE.md** for architecture details
2. Check **README.md** for feature overview
3. Review **DEPLOYMENT.md** for production setup
4. Run tests: `python manage.py test`
5. Start the server: `python manage.py runserver`

