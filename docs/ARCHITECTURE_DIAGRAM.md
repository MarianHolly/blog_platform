# Docker & Application Architecture Diagram

## What Runs When You Execute `docker-compose up`

```
┌────────────────────────────────────────────────────────────────┐
│                     DOCKER COMPOSE                              │
│                    (docker-compose.yml)                         │
└────────────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────┐      ┌──────────┐       ┌──────────┐
    │   WEB   │      │ DATABASE │       │  CACHE   │
    │ (Django)│      │ (PostgreSQL)     │  (Redis) │
    └─────────┘      └──────────┘       └──────────┘
    Port: 8000       Port: 5432         Port: 6379

    Your blog      Stores articles,    Caches pages,
    application   users, comments      stores sessions
```

---

## What Happens When You Start It

```
1. You type: docker-compose up

2. Docker reads docker-compose.yml and starts 3 containers:

   ┌─────────────────────────────────────────────┐
   │ Container 1: PostgreSQL Database            │
   │ - Starts first                              │
   │ - Waits for health check to pass            │
   │ - Initializes empty database                │
   └─────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────┐
   │ Container 2: Redis Cache                    │
   │ - Starts in parallel                        │
   │ - Ready immediately                         │
   │ - Stores sessions and cached data           │
   └─────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────┐
   │ Container 3: Django Web App                 │
   │ - Waits for postgres & redis to be ready    │
   │ - Installs Python dependencies              │
   │ - Runs: python manage.py migrate            │
   │ - Runs: python manage.py runserver 0.0.0.0:8000  │
   │ - App is now accessible!                    │
   └─────────────────────────────────────────────┘

3. You see: "Starting development server at http://127.0.0.1:8000/"

4. You open browser to http://localhost:8000
```

---

## Network Communication Inside Docker

```
Your Computer                Docker World
───────────────────────────────────────────────────────────────

┌──────────────────┐
│  Your Browser    │
│ localhost:8000   │
└────────┬─────────┘
         │
         │ http://localhost:8000
         │
         ▼
    ┌────────────────────────────────────────────┐
    │     Docker Network "blog-platform"         │
    │                                            │
    │  ┌──────────────┐                         │
    │  │    Django    │                         │
    │  │   :8000      │                         │
    │  └──────┬───────┘                         │
    │         │                                  │
    │    ┌────┴────────────┐                    │
    │    │                 │                    │
    │    ▼                 ▼                    │
    │  ┌──────────┐    ┌────────┐              │
    │  │PostgreSQL│    │ Redis  │              │
    │  │ :5432    │    │ :6379  │              │
    │  └──────────┘    └────────┘              │
    │                                            │
    └────────────────────────────────────────────┘
         │
         └─ Internal DNS resolution
            "postgres" → PostgreSQL container
            "redis" → Redis container
```

**Key Point**: Inside Docker, containers talk to each other by service name:
- Django connects to `postgres:5432` (not localhost:5432)
- Django connects to `redis:6379` (not localhost:6379)

This is why your `.env` has:
```env
DB_HOST=postgres        # Not "localhost"!
REDIS_URL=redis://redis:6379/0  # Not localhost!
```

---

## Data Storage & Persistence

```
Your Computer                       Docker Volumes (Persist)
─────────────────────────────────────────────────────────────

                            ┌──────────────────────┐
                            │  postgres_data       │
                            │  (Docker Volume)     │
                            │                      │
                            │  - Articles          │
PostgreSQL Container ───────→ - Users             │
                            │ - Comments           │
                            │ - Profiles           │
                            └──────────────────────┘

                            ┌──────────────────────┐
                            │  redis_data          │
                            │  (Docker Volume)     │
                            │                      │
                            │  - Cache data        │
Redis Container ────────────→ - Session tokens    │
                            │ - Temporary data     │
                            └──────────────────────┘
```

**What happens when you stop?**
- `docker-compose down` → Containers stop, but data persists in volumes
- `docker-compose up` → Containers restart, data is still there
- `docker-compose down -v` → Containers stop AND volumes deleted (fresh start)

---

## How Django Talks to Database

```
┌─────────────────────────────────────────────────────────────┐
│  Django Web Container                                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Your Code (views.py, models.py, etc)              │  │
│  │                                                      │  │
│  │  Article.objects.all()  # Get all articles         │  │
│  └─────────────────────────────────────────────────────┘  │
│            │                                               │
│            ▼                                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Django ORM (Object Relational Mapping)             │  │
│  │  Translates Python to SQL                           │  │
│  └─────────────────────────────────────────────────────┘  │
│            │                                               │
│            ▼                                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  psycopg (PostgreSQL driver)                        │  │
│  │  Opens connection to postgresql://postgres@postgres │  │
│  └─────────────────────────────────────────────────────┘  │
│            │                                               │
└────────────┼───────────────────────────────────────────────┘
             │
             │ SQL Query over network
             │
             ▼
    ┌─────────────────────┐
    │ PostgreSQL Container│
    │                     │
    │ SELECT * FROM      │
    │ content_article     │
    └─────────────────────┘
             │
             │ Results back
             ▼
    Returns: [Article1, Article2, ...]
```

---

## Your .env and Environment Variables

```
┌─────────────────────────────────────────────────────────────┐
│  .env File (In Your Project Root)                          │
│                                                             │
│  SECRET_KEY=abc123...                                       │
│  DEBUG=True                                                 │
│  DATABASE_URL=postgresql://postgres:postgres@postgres...  │
│  REDIS_URL=redis://redis:6379/0                           │
│  CLOUDINARY_CLOUD_NAME=...                                │
│  SUPERUSER_USERNAME=admin                                 │
│  SUPERUSER_PASSWORD=admin123                              │
└─────────────────────────────────────────────────────────────┘
         │
         │ docker-compose.yml loads it
         │
         ▼
    ┌─────────────────────────────────────────────────────────┐
    │  Docker Container Environment                          │
    │  (Available to Python code as os.environ)              │
    └─────────────────────────────────────────────────────────┘
         │
         │ settings.py reads them
         │
         ▼
    ┌─────────────────────────────────────────────────────────┐
    │  Django Settings                                        │
    │                                                         │
    │  DEBUG = os.getenv("DEBUG") = True                    │
    │  SECRET_KEY = os.getenv("SECRET_KEY") = "abc123..."  │
    │  DATABASES = { ...postgresql://postgres@postgres... } │
    │  CACHES = { ...redis://redis:6379/0... }             │
    └─────────────────────────────────────────────────────────┘
```

---

## Article Request Flow

```
User types: http://localhost:8000/articles/1/

    ▼

┌─────────────────────────────────┐
│  Django URL Router              │
│  (urls.py)                      │
└─────────────────────────────────┘
    │ Matches: article/<int:pk>/
    ▼
┌─────────────────────────────────┐
│  View (ArticleDetailView)       │
│  (views.py)                     │
└─────────────────────────────────┘
    │ Calls: Article.objects.get(pk=1)
    ▼
┌─────────────────────────────────┐
│  Django ORM                     │
└─────────────────────────────────┘
    │ Runs SQL: SELECT * FROM content_article WHERE id = 1
    ▼
┌─────────────────────────────────┐
│  PostgreSQL Database            │
│  Finds article #1               │
└─────────────────────────────────┘
    │ Returns: Article data
    ▼
┌─────────────────────────────────┐
│  View continues                 │
│  Renders template with data     │
└─────────────────────────────────┘
    │ Returns: HTML
    ▼
┌─────────────────────────────────┐
│  Browser receives HTML          │
│  Displays article               │
└─────────────────────────────────┘
```

---

## Caching with Redis

```
┌──────────────────────────────────────┐
│  Homepage Request (expensive query)  │
└──────────────────────────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Is it cached?   │
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        │                 │
       YES                NO
        │                 │
        ▼                 ▼
    ┌─────────┐    ┌──────────────────────┐
    │  Redis  │    │  Query Database      │
    │  Cache  │    │                      │
    │         │    │  - Get 9 articles    │
    │Returns  │    │  - Get 3 bulletins   │
    │ data    │    │  - Get 3 writers     │
    │ fast!   │    └──────────────────────┘
    └────┬────┘            │
         │                 │ Process results
         │                 ▼
         │          ┌──────────────────┐
         │          │  Cache Result    │
         │          │  in Redis        │
         │          │  (1 minute TTL)  │
         │          └──────────────────┘
         │                 │
         └────────┬────────┘
                  │
                  ▼
        ┌─────────────────┐
        │ Return to User  │
        └─────────────────┘
```

**TTL = Time To Live** - How long Redis keeps the data before forgetting it.

---

## File Structure Inside Container

```
Docker Container: Django App
─────────────────────────────────────────────

/app                           (WORKDIR from Dockerfile)
├── manage.py                  (Django management)
├── requirements.txt           (Python packages)
├── blog_platform/
│   ├── settings.py           (Configuration - reads .env)
│   ├── urls.py               (URL routing)
│   └── ...
├── accounts/
│   ├── models.py             (User & Profile)
│   ├── views.py
│   ├── tests.py
│   └── ...
├── content/
│   ├── models.py             (Article, Bulletin)
│   ├── views.py
│   ├── tests.py
│   └── ...
├── engagement/
│   ├── models.py             (Like, Comment, ReadLater)
│   ├── views.py
│   └── ...
├── templates/                (HTML templates)
├── static/                    (CSS, JS, images)
├── .env                       (Loaded from docker-compose.yml)
└── ...
```

---

## Traffic Flow Summary

```
┌──────────────────────────────────────────────────────────┐
│                    Your Computer                         │
│                                                          │
│  ┌─────────────┐                    ┌──────────────┐   │
│  │   Browser   │ ←→ localhost:8000   │ Docker       │   │
│  │ You browse  │                    │              │   │
│  │ articles    │                    │ ┌──────────┐ │   │
│  └─────────────┘                    │ │ Django   │ │   │
│                                     │ │ App      │ │   │
│                                     │ └─────┬────┘ │   │
│                                     │       │      │   │
│                                     │ ┌─────▼────┐ │   │
│                                     │ │PostgreSQL│ │   │
│                                     │ │Database  │ │   │
│                                     │ └──────────┘ │   │
│                                     │              │   │
│                                     │ ┌──────────┐ │   │
│                                     │ │ Redis    │ │   │
│                                     │ │ Cache    │ │   │
│                                     │ └──────────┘ │   │
│                                     └──────────────┘   │
│                                                        │
└──────────────────────────────────────────────────────┘
```

---

## Lifecycle When You Press Ctrl+C

```
You press: Ctrl+C

    ▼

docker-compose receives SIGINT signal

    ▼

Stops containers gracefully:
1. Django server stops accepting requests
2. PostgreSQL flushes data to disk
3. Redis saves state to volume
4. Containers shut down

    ▼

Your terminal shows:
Gracefully stopping... (max wait 10 seconds)

    ▼

All containers stopped

    ▼

Data is still in volumes (safe!)

    ▼

Next time: docker-compose up
→ Containers restart
→ Data is loaded from volumes
→ Everything picks up where it left off
```

---

## Summary: What You Need to Know

1. **Three Services Run Together**:
   - Django (your app)
   - PostgreSQL (database)
   - Redis (cache)

2. **They Communicate by Service Name**:
   - Django → postgres:5432
   - Django → redis:6379
   - Not localhost (that's your computer, not the containers)

3. **Data Persists**:
   - Volumes save database and cache data
   - Even when you stop, data is safe
   - Next time you start, data is there

4. **.env Sets Configuration**:
   - Tells Django how to connect
   - Sets admin password
   - Sets debug mode
   - Don't share this file (has secrets!)

5. **You Only Type One Command**:
   - `docker-compose up` → Everything starts
   - `Ctrl+C` → Everything stops
   - `docker-compose down -v` → Wipe everything

That's it! Understanding this diagram helps you troubleshoot when something goes wrong.
