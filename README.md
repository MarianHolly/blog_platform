# Blog Platform

A modern Django-based content management system for writers to publish articles and readers to engage with content through subscriptions, likes, and comments.

**Tech Stack**: Django 5.2 · Django REST Framework · PostgreSQL · Redis · Cloudinary · Tailwind CSS · CKEditor5

---

## Quick Links

| Document | Purpose |
|----------|---------|
| **[DEVELOPMENT.md](DEVELOPMENT.md)** | Local development setup and workflow |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Deploy to Railway with PostgreSQL & Redis |
| **[CLAUDE.md](CLAUDE.md)** | Architecture, models, permissions (for developers) |
| **[NOTES.md](NOTES.md)** | Detailed feature overview and user flows |

---

## Quick Start

### Local Development (5 minutes)
```bash
# 1. Clone and setup
git clone https://github.com/yourusername/blog_platform.git
cd blog_platform
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure .env
# Copy example and fill in your details
cp .env.example .env

# 3. Database setup
python manage.py migrate
python manage.py createsuperuser
python manage.py generate_mock_data  # Optional: Generate sample content

# 4. Run server
python manage.py runserver
# Visit http://localhost:8000
```

### Deploy to Railway (10 minutes)
See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete Railway setup guide.

---

## API Documentation

The platform provides a comprehensive RESTful API built with Django REST Framework.

### Base URL
```
http://localhost:8000/api/v1/
```

### Authentication
The API uses JWT (JSON Web Token) authentication:

```bash
# Get access token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Response:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
# }

# Use token in requests
curl http://localhost:8000/api/v1/articles/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Refresh token when expired
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

### Interactive API Documentation
Visit these URLs when the server is running:
- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/

### Main Endpoints

#### Articles
- `GET /api/v1/articles/` - List all public articles (supports filtering, search, pagination)
- `GET /api/v1/articles/{slug}/` - Get article details
- `POST /api/v1/articles/` - Create article (writers only)
- `PUT /api/v1/articles/{slug}/` - Update article (owner only)
- `DELETE /api/v1/articles/{slug}/` - Delete article (owner only)
- `POST /api/v1/articles/{slug}/like/` - Like/unlike article
- `POST /api/v1/articles/{slug}/bookmark/` - Bookmark/unbookmark article

#### Bulletins
- `GET /api/v1/bulletins/` - List all bulletins
- `GET /api/v1/bulletins/{slug}/` - Get bulletin details with articles
- `POST /api/v1/bulletins/{slug}/subscribe/` - Subscribe/unsubscribe to bulletin

#### Comments
- `GET /api/v1/comments/` - List comments (filter by article)
- `POST /api/v1/comments/` - Create comment
- `PUT /api/v1/comments/{id}/` - Update comment (author only)
- `DELETE /api/v1/comments/{id}/` - Delete comment (author only)

#### Bookmarks
- `GET /api/v1/bookmarks/` - List user's bookmarked articles

### Query Parameters

**Filtering:**
```bash
# Filter articles by status
GET /api/v1/articles/?status=published

# Filter by bulletin
GET /api/v1/articles/?bulletin=tech-bulletin

# Filter comments by article
GET /api/v1/comments/?article=5
```

**Search:**
```bash
# Search articles by title, subtitle, or content
GET /api/v1/articles/?search=django
```

**Ordering:**
```bash
# Order by created date (newest first)
GET /api/v1/articles/?ordering=-created

# Order by title
GET /api/v1/articles/?ordering=title
```

**Pagination:**
```bash
# Default: 20 items per page
GET /api/v1/articles/?page=2

# Custom page size
GET /api/v1/articles/?page_size=50
```

### Example Responses

**Article List:**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "slug": "getting-started-with-django",
      "title": "Getting Started with Django",
      "subtitle": "A comprehensive guide",
      "bulletin": {
        "slug": "tech-bulletin",
        "title": "Tech Bulletin"
      },
      "author": {
        "username": "john_writer",
        "full_name": "John Doe"
      },
      "created": "2024-02-15T10:30:00Z",
      "published": "2024-02-15T12:00:00Z",
      "likes_count": 15,
      "comments_count": 3
    }
  ]
}
```

---

## Mock Data Generation

Generate realistic sample data to populate your blog platform for development and testing:

### Basic Usage
```bash
# Generate default data (30 users, 50 articles)
python manage.py generate_mock_data

# Generate more data for demos
python manage.py generate_mock_data --users 100 --articles 200

# Clear existing data and regenerate
python manage.py generate_mock_data --clear
```

### What Gets Created
- **Users**: 20% writers, 80% readers
- **Bulletins**: One per writer with description
- **Articles**: Realistic HTML content (80% published, 20% draft)
- **Subscriptions**: Readers subscribe to 2-5 random bulletins
- **Engagement**: Random likes, comments, and bookmarks

**Note:** All generated users have the password `password123`

### View Generated Content
```bash
# List generated writers
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(profile__role='writer').values_list('username', flat=True)[:5]

# Check article count
>>> from content.models import Article
>>> Article.objects.filter(status='published').count()
```

---

## Features

### User Roles
- **Readers**: Subscribe to writers, like/comment on articles, save for later
- **Writers**: Create personal bulletins, publish articles, manage content
- **Administrators**: Moderate articles, verify content, manage platform

### Content Management
- **Rich Text Editor**: CKEditor5 with sanitized HTML output
- **Draft & Publish**: Articles can be draft (private) or published (public)
- **Visibility Control**: Articles can be public (everyone) or private (subscribers only)
- **Evaluation Workflow**: Admin can approve/reject articles during review

### Engagement
- **Likes**: React to articles (logged-in users only)
- **Comments**: Discuss articles with one comment per user per article
- **Read Later**: Bookmark articles for later reading
- **Subscriptions**: Follow writers to access their private content

---

## System Architecture

### Database Models

```
User (Django)
  └─ Profile (OneToOne) [role: reader|writer|admin]
      └─ Bulletin (OneToOne if writer)
          └─ Article (ForeignKey)
              ├─ Comments (1:many)
              ├─ Likes (1:many)
              └─ ReadLater (1:many)

Subscription [Profile → Bulletin] - Links readers to writer bulletins
```

### Permissions

| Action | Visitor | Reader | Writer | Admin |
|--------|---------|--------|--------|-------|
| View public articles | ✓ | ✓ | ✓ | ✓ |
| Like articles | ✗ | ✓ | ✓ | ✓ |
| Create articles | ✗ | ✗ | ✓ | ✗ |
| Moderate articles | ✗ | ✗ | ✗ | ✓ |
| Access private articles | ✗ | If subscribed | Own only | All |

---

## Project Structure

```
blog_platform/
├── accounts/           # Authentication & profiles
├── content/            # Articles & bulletins
├── engagement/         # Likes, comments, bookmarks
├── core/               # Shared utilities
├── templates/          # Django templates
├── static/             # CSS, JavaScript
├── requirements.txt    # Python dependencies
├── manage.py           # Django CLI
└── .env.example        # Environment template
```

---

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app
python manage.py test accounts

# With coverage
coverage run --source='.' manage.py test
coverage report
```

---

## Admin Panel

Access Django admin at `/admin`:
- Create/edit users
- Manage roles (promote to writer/admin)
- Create bulletins
- Review and evaluate articles

View admin dashboard at `/accounts/admin-dashboard`:
- See articles pending review
- View evaluation history

---

## Environment Configuration

Create `.env` file with:
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://user:password@localhost:5432/blog_platform

REDIS_URL=redis://localhost:6379/0

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=secure-password
```

See `.env.example` for complete template.

---

## Key Features in Development

- ✅ **RESTful API** with Django REST Framework + JWT authentication
- ✅ **Interactive API docs** with Swagger UI and ReDoc
- ✅ **Multi-role system** with permission mixins
- ✅ **Content sanitization** prevents XSS attacks
- ✅ **Article evaluation workflow** for moderation
- ✅ **Subscription model** for private content
- ✅ **Mock data generator** for testing and demos
- ✅ **Responsive design** with Tailwind CSS
- ✅ **Media storage** via Cloudinary
- ✅ **Redis caching** for performance
- ✅ **Comprehensive tests** for all apps

---

## Performance Optimizations

- **Database indexes** on frequently queried fields (Like, Comment, ReadLater)
- **Select/prefetch related** in admin to avoid N+1 queries
- **Redis caching** for homepage and bulletin queries
- **Static file optimization** with WhiteNoise
- **HTML sanitization** with bleach library

---

## Documentation by Role

### For Developers
- **[DEVELOPMENT.md](DEVELOPMENT.md)**: Setup, testing, common tasks
- **[CLAUDE.md](CLAUDE.md)**: Architecture decisions, code patterns

### For DevOps/Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Railway setup, environment config, troubleshooting

### For Product Managers
- **[NOTES.md](NOTES.md)**: User flows, feature descriptions, future roadmap

---

## Troubleshooting

### Can't Connect to Database
```bash
# Check PostgreSQL is running
# Windows: services.msc → PostgreSQL
# macOS: brew services start postgresql

# Verify DATABASE_URL in .env
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Tests Failing
```bash
python manage.py test --verbosity=2
# Check test output for specific errors
```

See **[DEVELOPMENT.md](DEVELOPMENT.md)** for more troubleshooting.

---

## License

This project is open source and available under the MIT License.

---

## Next Steps

1. **New to the project?** → Start with [DEVELOPMENT.md](DEVELOPMENT.md)
2. **Ready to deploy?** → Follow [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Need architecture details?** → Read [CLAUDE.md](CLAUDE.md)
4. **Want feature overview?** → Check [NOTES.md](NOTES.md)
