# Data Models

## Entity Relationship

```
User (Django built-in)
 └── Profile (1:1)
      ├── role: reader | writer | admin
      └── Bulletin (1:1, writer only)
           └── Article (1:many)
                ├── Comment (1:many)   ← authored by Profile
                ├── Like (1:many)      ← authored by Profile
                └── ReadLater (1:many) ← authored by Profile

Profile ──[Subscription]── Bulletin   (many-to-many via junction)
```

---

## Profile

Extends Django's built-in `User` via `OneToOneField`.

| Field | Type | Notes |
|---|---|---|
| `user` | OneToOneField(User) | Linked Django user |
| `role` | CharField | `reader` \| `writer` \| `admin` |
| `biography` | TextField | Max 500 chars, optional |
| `avatar` | ImageField | Stored on Cloudinary, falls back to ui-avatars.com |
| `auto_subscribed_to_platform` | BooleanField | Platform-level subscription flag |

**Computed properties:**
- `full_name` — `first_name last_name` or `username` fallback
- `avatar_url` — Cloudinary URL or generated initials avatar
- `is_reader / is_writer / is_admin` — role shortcuts

**Ordering:** alphabetical by username

---

## Bulletin

A writer's personal publication channel. Each writer has exactly one bulletin.

| Field | Type | Notes |
|---|---|---|
| `owner` | OneToOneField(Profile) | Must be a writer |
| `title` | CharField | Max 255, unique |
| `slug` | SlugField | Max 295, unique, auto-generated |
| `description` | TextField | Optional |
| `created` | DateTimeField | Auto |
| `updated` | DateTimeField | Auto |

---

## Article

The primary content unit. Belongs to a bulletin (and therefore has an author via `bulletin.owner`).

| Field | Type | Notes |
|---|---|---|
| `title` | CharField | Max 150, unique within bulletin |
| `slug` | SlugField | Max 200, globally unique, auto-generated from title |
| `subtitle` | CharField | Max 200, optional |
| `description` | TextField | Optional short summary |
| `content` | CKEditor5Field | Rich HTML, sanitized on save |
| `bulletin` | ForeignKey(Bulletin) | Cascade delete |
| `status` | CharField | `draft` \| `published` |
| `visibility` | CharField | `public` \| `private` |
| `evaluation` | CharField | `pending` \| `under_review` \| `approved` \| `rejected` |
| `created` | DateTimeField | Auto |
| `published` | DateTimeField | Set automatically when status → published |
| `updated` | DateTimeField | Auto |

**Computed properties:**
- `author` — `bulletin.owner` (Profile)
- `is_draft / is_published_public / is_published_private`
- `is_approved / is_rejected`

**Content sanitization:** `bleach` removes XSS vectors on every save. Allowed tags include `p, strong, em, h1-h6, a, img, blockquote, code, pre, table, ul, ol, li, div, span, figure`.

**Database indexes:**
- `(status, visibility, evaluation)` — main listing query
- `(bulletin, status)` — bulletin page query
- `(evaluation, created)` — admin moderation queue

**Ordering:** newest first (`-created`)

---

## Subscription

Junction model linking a reader Profile to a Bulletin.

| Field | Type | Notes |
|---|---|---|
| `subscriber` | ForeignKey(Profile) | The reader |
| `bulletin` | ForeignKey(Bulletin) | The bulletin followed |
| `created` | DateTimeField | Auto |

**Constraint:** `unique_together(subscriber, bulletin)` — one subscription per pair.

---

## Comment

| Field | Type | Notes |
|---|---|---|
| `author` | ForeignKey(Profile) | Commenter |
| `article` | ForeignKey(Article) | Target article |
| `content` | TextField | Max 500 chars |
| `created` | DateTimeField | Auto |
| `updated` | DateTimeField | Auto |

**Constraint:** `unique_together(author, article)` — one comment per user per article.

**Indexes:** on `article`, on `author`.

---

## Like

| Field | Type | Notes |
|---|---|---|
| `author` | ForeignKey(Profile) | Who liked |
| `article` | ForeignKey(Article) | What was liked |
| `created` | DateTimeField | Auto |

**Constraint:** `unique_together(author, article)` — one like per user per article.

---

## ReadLater (Bookmark)

| Field | Type | Notes |
|---|---|---|
| `author` | ForeignKey(Profile) | Who bookmarked |
| `article` | ForeignKey(Article) | What was bookmarked |
| `created` | DateTimeField | Auto |

**Constraint:** `unique_together(author, article)` — one bookmark per user per article.

---

## Visibility and Access Rules

| User | Can see |
|---|---|
| Anonymous | Published + public articles only |
| Reader | Published public + published private in subscribed bulletins |
| Writer | Own articles (any status) + published public articles |
| Admin | All articles regardless of status or visibility |

These rules are enforced in `ArticleViewSet.get_queryset()`.
