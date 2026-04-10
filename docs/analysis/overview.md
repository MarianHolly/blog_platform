# Project Overview

## What it is

A multi-author blog platform where writers publish articles inside their personal **bulletin** (a named publication channel), and readers subscribe to bulletins, like articles, comment, and bookmark content for later.

The project is structured as a **monorepo** with a Django REST API backend and an Astro SSR frontend.

---

## Repository Structure

```
blog_platform/
├── backend/          Django REST API + admin
├── frontend/         Astro SSR frontend
├── docs/             Project documentation
│   └── analysis/     Technical analysis and reference
└── docker-compose.yml
```

---

## Tech Stack

### Backend (`backend/`)

| Layer | Technology |
|---|---|
| Framework | Django 5.2 |
| API | Django REST Framework 3.15 |
| Auth | JWT via `djangorestframework-simplejwt` |
| API docs | drf-spectacular (Swagger UI + ReDoc) |
| Database | PostgreSQL (psycopg3) |
| Cache | Redis (optional, falls back to dummy cache) |
| Media storage | Cloudinary |
| Rich text | CKEditor 5 |
| HTML sanitization | bleach |
| CORS | django-cors-headers |
| Static files | WhiteNoise |
| Task queue | Celery (installed, not yet wired to tasks) |

### Frontend (`frontend/`)

| Layer | Technology |
|---|---|
| Framework | Astro 6 |
| Rendering | SSR (`output: 'server'`) |
| Styling | Tailwind CSS 4 |
| Language | TypeScript (strict) |
| Package manager | pnpm |

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 22+
- pnpm
- PostgreSQL running on port 5432
- Redis running on port 6379 (optional)

### Start backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in values
python manage.py migrate
python manage.py generate_mock_data   # optional sample data
python manage.py runserver            # → http://localhost:8000
```

### Start frontend
```bash
cd frontend
pnpm install
cp .env.example .env        # PUBLIC_API_URL=http://localhost:8000
pnpm dev                    # → http://localhost:4321
```

### Docker (runs everything)
```bash
docker compose up
```

### Key URLs

| URL | Description |
|---|---|
| `http://localhost:4321` | Astro frontend |
| `http://localhost:8000/admin/` | Django admin |
| `http://localhost:8000/api/v1/` | REST API root |
| `http://localhost:8000/api/v1/docs/` | Swagger UI |

---

## Environment Variables

### `backend/.env`

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | yes | Django secret key |
| `DEBUG` | yes | `True` for local |
| `ALLOWED_HOSTS` | yes | Comma-separated hosts |
| `DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT` | yes | PostgreSQL connection |
| `DATABASE_URL` | alt | Single-string alternative to individual DB vars |
| `REDIS_URL` | no | Falls back to dummy cache |
| `CLOUDINARY_CLOUD_NAME / API_KEY / API_SECRET` | yes | Media storage |
| `FRONTEND_URL` | no | Added to CORS allowed origins |
| `SUPERUSER_USERNAME / EMAIL / PASSWORD` | no | Auto-created on first deploy |

### `frontend/.env`

| Variable | Required | Description |
|---|---|---|
| `PUBLIC_API_URL` | yes | Django base URL, e.g. `http://localhost:8000` |
