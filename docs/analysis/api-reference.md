# API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/api/v1/docs/`

All list endpoints return paginated responses (20 items per page by default).

---

## Authentication

### Obtain tokens
```
POST /auth/token/
Body: { "username": "...", "password": "..." }
Response: { "access": "<jwt>", "refresh": "<jwt>" }
```

### Refresh access token
```
POST /auth/token/refresh/
Body: { "refresh": "<jwt>" }
Response: { "access": "<jwt>" }
```

Use the access token in all authenticated requests:
```
Authorization: Bearer <access>
```

---

## Articles

### List articles
```
GET /articles/
```

**Query parameters:**

| Param | Type | Description |
|---|---|---|
| `page` | int | Page number |
| `page_size` | int | Items per page (default 20) |
| `search` | string | Search title, subtitle, content |
| `status` | string | `draft` \| `published` |
| `visibility` | string | `public` \| `private` |
| `bulletin` | int | Filter by bulletin ID |
| `ordering` | string | `created`, `published`, `title` (prefix `-` for descending) |

**Response:**
```json
{
  "count": 50,
  "next": "/api/v1/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "slug": "my-first-article",
      "title": "My First Article",
      "subtitle": "A short description",
      "description": "Optional summary",
      "bulletin_title": "Tech Bulletin",
      "author": { "id": 2, "username": "jane", "full_name": "Jane Doe", "avatar_url": "..." },
      "status": "published",
      "visibility": "public",
      "likes_count": 12,
      "comments_count": 3,
      "created": "2026-01-15T10:00:00Z",
      "published": "2026-01-15T12:00:00Z"
    }
  ]
}
```

### Get article detail
```
GET /articles/{slug}/
```

Returns everything from the list response plus:
```json
{
  "content": "<p>Full HTML content...</p>",
  "evaluation": "approved",
  "updated": "2026-01-16T08:00:00Z",
  "is_liked": false,
  "is_bookmarked": false,
  "can_edit": false
}
```

### Create article *(writer only)*
```
POST /articles/
Authorization: Bearer <token>
Body: { "title": "...", "subtitle": "...", "content": "...", "status": "draft", "visibility": "public" }
```
Bulletin is automatically set to the writer's own bulletin.

### Update article *(owner only)*
```
PUT /articles/{slug}/
PATCH /articles/{slug}/
Authorization: Bearer <token>
```

### Delete article *(owner only)*
```
DELETE /articles/{slug}/
Authorization: Bearer <token>
```

### Like / unlike article *(authenticated)*
```
POST /articles/{slug}/like/
Authorization: Bearer <token>
Response: { "status": "liked" } or { "status": "unliked" }
```

### Bookmark / unbookmark article *(authenticated)*
```
POST /articles/{slug}/bookmark/
Authorization: Bearer <token>
Response: { "status": "bookmarked" } or { "status": "removed" }
```

---

## Bulletins

### List bulletins
```
GET /bulletins/
```

| Param | Description |
|---|---|
| `search` | Search title, description |
| `ordering` | `created`, `title` |

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "slug": "tech-bulletin",
      "title": "Tech Bulletin",
      "description": "Articles about technology",
      "owner": { ... },
      "subscribers_count": 42,
      "articles_count": 15,
      "created": "2026-01-01T00:00:00Z",
      "updated": "2026-01-20T00:00:00Z"
    }
  ]
}
```

### Get bulletin detail
```
GET /bulletins/{slug}/
```

Returns list fields plus:
```json
{
  "recent_articles": [ ... ]   // 5 most recent published articles
}
```

### Subscribe / unsubscribe *(authenticated reader)*
```
POST /bulletins/{slug}/subscribe/
Authorization: Bearer <token>
Response: { "status": "subscribed" } or { "status": "unsubscribed" }
```
Writers cannot subscribe to bulletins.

---

## Comments

### List comments
```
GET /comments/?article={id}
Authorization: Bearer <token>
```

### Create comment *(authenticated)*
```
POST /comments/
Authorization: Bearer <token>
Body: { "article": 5, "content": "Great article!" }
```
One comment per user per article — returns 400 if already commented.

### Update comment *(author only)*
```
PUT /comments/{id}/
PATCH /comments/{id}/
Authorization: Bearer <token>
```

### Delete comment *(author only)*
```
DELETE /comments/{id}/
Authorization: Bearer <token>
```

---

## Bookmarks (Read Later)

### List bookmarks
```
GET /bookmarks/
Authorization: Bearer <token>
```

### Add bookmark
```
POST /bookmarks/
Authorization: Bearer <token>
Body: { "article": 5 }
```

### Remove bookmark
```
DELETE /bookmarks/{id}/
Authorization: Bearer <token>
```

---

## Subscriptions

### List subscriptions
```
GET /subscriptions/
Authorization: Bearer <token>
```

### Create subscription
```
POST /subscriptions/
Authorization: Bearer <token>
Body: { "bulletin_id": 3 }
```

### Delete subscription
```
DELETE /subscriptions/{id}/
Authorization: Bearer <token>
```

---

## Pagination

All list endpoints return:
```json
{
  "count": 100,
  "next": "/api/v1/articles/?page=3",
  "previous": "/api/v1/articles/?page=1",
  "results": [ ... ]
}
```

Default page size: **20**. Override with `?page_size=50` (max not enforced currently).
