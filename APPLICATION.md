# Application Documentation - Blog Platform

Complete technical documentation of the Blog Platform application, explaining every component, feature, and how they work together.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [User Roles & Permissions](#user-roles--permissions)
3. [Data Models](#data-models)
4. [Features Overview](#features-overview)
5. [Application Flow](#application-flow)
6. [API & View Documentation](#api--view-documentation)
7. [Database Schema](#database-schema)
8. [Configuration](#configuration)

---

## Core Concepts

### What is Blog Platform?

Blog Platform is a Django-based content management system that enables:
- **Writers** to publish articles and manage personal bulletins
- **Readers** to discover articles, subscribe to writers, and engage through likes/comments
- **Administrators** to moderate content and ensure platform safety

Think of it like Medium.com, but with role-based permissions and content moderation.

### Key Architectural Decisions

1. **Bulletin Model**: Writers don't publish directly; they publish through a personal "Bulletin" (like a publication). This separates content organization from user identity.

2. **One Profile Per User**: Each Django User gets a OneToOne Profile with a role field (reader/writer/admin). This avoids Django's multiple inheritance issues.

3. **Role Isolation**: Roles are mutually exclusive. You can't be both a writer and admin at the same time. This simplifies permission logic.

4. **Article Ownership via Bulletin**: Writers can only edit articles in their own bulletin. This is enforced by ArticleOwnerMixin even for superusers.

5. **Evaluation Separate from Publishing**: Articles have two independent workflows:
   - Status: draft → published (controlled by writer)
   - Evaluation: pending → under_review → approved/rejected (controlled by admin)

---

## User Roles & Permissions

### 1. Visitor (Unauthenticated User)

Permissions:
- View all public articles
- View bulletin pages
- View writer profiles
- Access signup/login pages

Restrictions:
- Cannot like articles
- Cannot comment
- Cannot create content

### 2. Reader

Permissions (all of Visitor + ):
- Create account with reader role
- View personal profile
- Like articles
- Comment on articles
- Save articles (read-later)
- Subscribe to writers
- View private articles of subscribed writers
- Upgrade to writer role

Restrictions:
- Cannot create articles
- Cannot moderate content
- Cannot access admin panel

### 3. Writer

Permissions (all of Reader + ):
- Create personal Bulletin
- Create articles
- Publish/draft articles
- Make articles public/private
- Edit own articles
- Delete own articles

Restrictions:
- Cannot edit other writers' articles
- Cannot moderate content
- Cannot access admin panel
- Cannot be admin (mutually exclusive)

### 4. Administrator

Permissions:
- View all articles (regardless of visibility)
- Review articles under evaluation
- Approve articles (mark as verified)
- Reject articles (hide and warn writer)
- Access admin panel (/admin)
- Access admin dashboard (/accounts/admin-dashboard)
- Create/edit/delete any user

Restrictions:
- Cannot write articles (admin role is separate from writer)
- No public bulletin/profile as writer

---

## Data Models

### Profile Model
- Extends Django User with OneToOne relationship
- Fields: role (reader|writer|admin), avatar, biography
- Cascade delete removes user when profile deleted

### Bulletin Model
- OneToOne with Profile (writers only)
- Fields: title, slug, description
- Each writer has exactly one bulletin
- Readers subscribe to bulletins, not writers

### Article Model
- ForeignKey to Bulletin
- Fields: title, slug, content, status, visibility, evaluation
- Status: draft (private) or published
- Visibility: public (everyone) or private (subscribers only)
- Evaluation: pending, under_review, approved, rejected
- Content auto-sanitizes on save (XSS prevention)

### Comment Model
- ForeignKey to Article and User
- Unique constraint: one comment per user per article
- Content sanitized like Article
- Supports edit/delete operations

### Like Model
- ForeignKey to Article and User
- Unique constraint: one like per user per article
- Users cannot like own articles (enforced in view)
- Indexed for fast queries

### ReadLater Model
- ForeignKey to Article and User
- Unique constraint: one bookmark per user per article
- Users cannot bookmark own articles
- Indexed on (user, created_at)

### Subscription Model
- ForeignKey to Profile (reader) and Bulletin (writer)
- Unique constraint: subscriber cannot subscribe twice
- Links readers to writer bulletins

---

## Features Overview

### 1. Article Lifecycle

Draft → Published → Admin Reviews → Approved/Rejected

**Writer Actions**:
- Create article (status=draft)
- Edit before publishing
- Publish (status=published)
- Set visibility (public/private)

**Admin Actions**:
- See article automatically in pending queue
- Review for safety/appropriateness
- Approve (visible to readers)
- Reject (hidden from readers, writer warned)

### 2. Engagement System

**Likes**:
- Readers like articles
- Cannot like own articles
- One like per user (toggle: like/unlike)

**Comments**:
- Readers comment on articles
- One comment per user (updatable)
- Can edit/delete own comment
- Content sanitized

**Read Later**:
- Bookmark articles for later
- One bookmark per user (toggle)
- Cannot bookmark own articles

### 3. Subscription Model

- Reader subscribes to writer's bulletin
- Grants access to private articles
- Can unsubscribe anytime
- Subscriptions are personal (not shared)

### 4. Content Search

- Full-text search by title and content
- Filter by writer, publication date
- Pagination for large result sets
- Results respect visibility permissions

---

## Application Flow

### New User Flow

1. Visitor signs up as reader
2. Explore public articles
3. Like, comment, bookmark articles
4. Discover writer → Subscribe to bulletin
5. Access writer's private articles

### Writer Flow

1. Reader decides to write
2. Click "Promote to Writer"
3. Bulletin created automatically
4. Create and publish article
5. Admin reviews → Approved/Rejected
6. Readers can now see and engage

### Admin Flow

1. Admin logs into /accounts/admin-dashboard/
2. See pending articles in queue
3. Review article for safety
4. Approve (visible to readers) or Reject (hidden)
5. Writer receives feedback

---

## API & View Documentation

### Authentication Views

**SignUpView** (POST /accounts/signup/)
- Register new user as reader
- Returns: Redirect to login

**LoginView** (POST /accounts/login/)
- Authenticate user via username/password
- Returns: Session cookie, redirect to home

**LogoutView** (GET /accounts/logout/)
- End user session
- Returns: Redirect to home

### Content Views

**HomeView** (GET /)
- Display articles (filtered by visibility + subscriptions)
- Cached 1 minute for performance
- Shows featured articles to visitors

**ArticleDetailView** (GET /articles/\<id\>/)
- Display full article with comments, likes
- Respects visibility permissions
- Shows comment form to authenticated users

**ArticleCreateView** (GET/POST /articles/create/)
- Create new article
- Requires: WriterRequiredMixin
- Returns: Article form or redirect on success

**ArticleUpdateView** (GET/POST /articles/\<id\>/edit/)
- Edit article content
- Requires: WriterRequiredMixin + ArticleOwnerMixin
- Returns: Article form with current values

**ArticleDeleteView** (POST /articles/\<id\>/delete/)
- Delete article (cascade deletes comments, likes)
- Requires: WriterRequiredMixin + ArticleOwnerMixin
- Returns: Redirect to bulletin

**BulletinDetailView** (GET /bulletins/\<slug\>/)
- Display writer's articles
- Filters by visibility (subscribers see private)
- Shows writer bio and article list

**ArticleSearchView** (GET /articles/search/)
- Full-text search
- Query param: q (search term)
- Returns: Filtered article list

### Engagement Views

**LikeToggleView** (POST /articles/\<id\>/like/)
- Like/unlike article
- Prevents self-engagement
- Returns: JSON with new like count

**ReadLaterToggleView** (POST /articles/\<id\>/save/)
- Bookmark/unbookmark article
- Prevents self-engagement
- Returns: JSON with bookmark status

**CommentCreateView** (POST /articles/\<id\>/comment/)
- Create or update comment
- One comment per user
- Returns: Redirect to article with comment

### Moderation Views

**AdminDashboardView** (GET /accounts/admin-dashboard/)
- Admin moderation interface
- Requires: AdministratorRequiredMixin
- Shows: Pending articles, approval history

**ArticleEvaluationView** (GET/POST /articles/\<id\>/evaluate/)
- Approve or reject article
- Requires: AdministratorRequiredMixin
- Returns: Evaluation form or redirect on success

**PromoteToWriterView** (POST /accounts/promote-writer/)
- Convert reader to writer
- Creates bulletin automatically
- Returns: Redirect to new bulletin

---

## Database Schema

### Core Tables

User (Django):
- username (unique)
- email
- password (hashed)
- is_active
- date_joined

Profile (OneToOne → User):
- role: reader | writer | admin
- avatar (Cloudinary)
- biography
- created_at, updated_at

Bulletin (OneToOne → Profile):
- title
- slug (unique)
- description
- created_at, updated_at

Article (FK → Bulletin):
- title
- slug
- content (sanitized HTML)
- status: draft | published
- visibility: public | private
- evaluation: pending | under_review | approved | rejected
- created_at, updated_at

Comment (FK → Article, FK → User):
- content (sanitized)
- created_at, updated_at
- Unique: (article, user)

Like (FK → Article, FK → User):
- created_at
- Unique: (article, user)
- Indexed: (article, user)

ReadLater (FK → Article, FK → User):
- created_at
- Unique: (article, user)
- Indexed: (user, created_at)

Subscription (FK → Profile, FK → Bulletin):
- Unique: (subscriber, bulletin)
- Links readers to writer bulletins

---

## Configuration

### Environment Variables

See .env.example for complete template.

**Required**:
- SECRET_KEY (generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
- DEBUG (True for dev, False for prod)
- ALLOWED_HOSTS (comma-separated)

**Database**:
- DATABASE_URL or (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)

**Storage**:
- CLOUDINARY_CLOUD_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET

**Superuser**:
- SUPERUSER_USERNAME
- SUPERUSER_EMAIL
- SUPERUSER_PASSWORD

**Optional**:
- REDIS_URL (for caching)
- EMAIL_* (for notifications)

---

## Performance Optimization

### Database Indexes

Added to engagement models (Like, Comment, ReadLater):
- (article, user) - For quick duplicate checks
- (user, created_at) - For user's recent bookmarks

### Query Optimization

Admin uses select_related to avoid N+1 queries:
```python
articles = Article.objects.select_related('bulletin__profile__user')
```

### Caching Strategy

- Homepage: 1-minute cache (aggregation is expensive)
- Bulletin articles: 10-minute cache
- Fallback: Database sessions if Redis unavailable

### Content Sanitization

HTML automatically sanitized on Article.save():
- Removes dangerous tags (script, iframe, event handlers)
- Whitelist: p, br, strong, em, u, ol, ul, li, h1-h3
- Prevents XSS attacks from rich editor input

---

## Common Workflows

### Creating an Article

1. Login as writer
2. Click "New Article"
3. Fill form: title, content, status, visibility
4. Submit → Article created (status=draft)
5. Publish → status=published, evaluation=pending
6. Admin reviews → evaluation=approved/rejected
7. If approved, visible to readers based on visibility setting

### Subscribing to Private Content

1. Discover writer on platform
2. Click "Subscribe" on bulletin page
3. Subscription created
4. Now can view writer's private articles
5. Can unsubscribe anytime

### Reviewing Content as Admin

1. Login as admin
2. Visit /accounts/admin-dashboard/
3. See articles with evaluation=pending
4. Click article to review
5. Read content, check for safety issues
6. Choose: Approve (verified) or Reject (inappropriate)
7. If approved: visible to readers. If rejected: hidden.

---

## Next Steps

- **Setup**: [DEVELOPMENT.md](DEVELOPMENT.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Architecture**: [CLAUDE.md](CLAUDE.md)
