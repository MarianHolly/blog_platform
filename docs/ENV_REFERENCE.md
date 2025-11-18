# Environment Variables Reference (.env)

This file explains each variable in your `.env` file and when you need to change them.

## Django Settings

### SECRET_KEY
```env
SECRET_KEY=your-secret-key-change-this-in-production-12345abcde
```
- **What it is**: Django's secret key used to encrypt sessions and cookies
- **Change for production**: YES, use a long random string
- **Generate one**: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- **Local development**: You can use the default

### DEBUG
```env
DEBUG=True
```
- **What it is**: Turns on debug mode (shows errors, auto-reload code)
- **Local development**: Set to `True` (you want to see errors)
- **Production**: Set to `False` (security risk to show errors)
- **Values**: `True` or `False`

### ALLOWED_HOSTS
```env
ALLOWED_HOSTS=localhost,127.0.0.1
```
- **What it is**: List of domain names that can access your app
- **Local development**: `localhost,127.0.0.1` is fine
- **Production**: Add your domain: `mysite.com,www.mysite.com,127.0.0.1`
- **Comma-separated**: No spaces between values

---

## Database Configuration

**Important**: These MUST match your docker-compose.yml! Don't change them unless you know what you're doing.

### DATABASE_URL
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
```
- **What it is**: Complete database connection string
- **Format**: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE`
- **Docker**: `postgres` is the service name (not localhost!)
- **Local (no Docker)**: Would be `postgresql://postgres:postgres@localhost:5432/postgres`
- **When to change**: Only if you use a different database name or credentials

### DB_NAME
```env
DB_NAME=postgres
```
- **What it is**: Database name
- **Docker**: Must be `postgres` (set in docker-compose.yml)
- **Should match**: `POSTGRES_DB` in docker-compose.yml

### DB_USER
```env
DB_USER=postgres
```
- **What it is**: Database username
- **Docker**: Must be `postgres` (set in docker-compose.yml)
- **Should match**: `POSTGRES_USER` in docker-compose.yml

### DB_PASSWORD
```env
DB_PASSWORD=postgres
```
- **What it is**: Database password
- **Docker**: Must be `postgres` (set in docker-compose.yml)
- **Should match**: `POSTGRES_PASSWORD` in docker-compose.yml
- **Production**: Change this to something secure!

### DB_HOST
```env
DB_HOST=postgres
```
- **What it is**: Where the database is running
- **Docker**: `postgres` (the service name in docker-compose.yml)
- **Local (no Docker)**: `localhost`
- **Remote**: Would be your RDS endpoint or IP

### DB_PORT
```env
DB_PORT=5432
```
- **What it is**: PostgreSQL default port
- **Almost always**: `5432` for PostgreSQL
- **Change only if**: You configured PostgreSQL on a different port

---

## Redis Cache Configuration

### REDIS_URL
```env
REDIS_URL=redis://redis:6379/0
```
- **What it is**: Connection string to Redis cache
- **Format**: `redis://HOST:PORT/DATABASE_NUMBER`
- **Docker**: `redis` is the service name (not localhost!)
- **Local (no Docker)**: Would be `redis://localhost:6379/0`
- **Database number**: `/0` at the end (0-15 available)
- **Optional**: If not set, app falls back to database sessions (slower but works)

**What Redis does**:
- Caches the homepage (faster loading)
- Stores session data (faster user logins)
- Optional - the app works without it!

---

## Cloudinary Configuration

### CLOUDINARY_CLOUD_NAME
```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
```
- **What it is**: Your Cloudinary account name
- **Need it?**: Only if you want to upload images/files
- **Get it**: Sign up at https://cloudinary.com
- **Optional**: You can leave commented out - the app works without it
- **What happens without it**: Image uploads won't work, but the app runs fine

### CLOUDINARY_API_KEY
```env
CLOUDINARY_API_KEY=your-api-key
```
- **What it is**: Public API key for Cloudinary
- **Need it?**: Only if using Cloudinary
- **Get it**: From your Cloudinary dashboard
- **Finding it**: Login → Settings → API → Copy "API Key"

### CLOUDINARY_API_SECRET
```env
CLOUDINARY_API_SECRET=your-api-secret
```
- **What it is**: Secret API key for Cloudinary
- **Need it?**: Only if using Cloudinary
- **Get it**: From your Cloudinary dashboard
- **Finding it**: Login → Settings → API → Copy "API Secret"
- **Warning**: Keep this secret! Don't commit to Git!

**For local development**: Comment out all three Cloudinary variables (add # at start of line)
```env
# CLOUDINARY_CLOUD_NAME=your-cloud-name
# CLOUDINARY_API_KEY=your-api-key
# CLOUDINARY_API_SECRET=your-api-secret
```

The app will work fine without them. When you're ready to add images:
1. Sign up for Cloudinary (free tier is enough)
2. Get the credentials
3. Add them to .env
4. Restart Docker

---

## Superuser (Admin Account)

### SUPERUSER_USERNAME
```env
SUPERUSER_USERNAME=admin
```
- **What it is**: Admin username
- **Created automatically**: When you run `docker-compose up` first time
- **Change it**: Set before first startup
- **After startup**: Can't easily change (would need database access)

### SUPERUSER_EMAIL
```env
SUPERUSER_EMAIL=admin@blogplatform.com
```
- **What it is**: Admin email address
- **Created automatically**: When you run `docker-compose up` first time
- **Change it**: Set before first startup
- **After startup**: Can change in Django admin panel

### SUPERUSER_PASSWORD
```env
SUPERUSER_PASSWORD=admin123
```
- **What it is**: Admin password
- **Created automatically**: When you run `docker-compose up` first time
- **Change it**: Set before first startup
- **Security**: For local development, any password is fine
- **Production**: Change to something secure!
- **After startup**: Can change in Django admin panel

**Example admin credentials**:
```env
SUPERUSER_USERNAME=maria
SUPERUSER_EMAIL=maria@example.com
SUPERUSER_PASSWORD=MySecurePassword123!
```

---

## Complete Example .env Files

### For Local Development (Simplest)
```env
# Django
SECRET_KEY=dev-key-not-secure-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Docker)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Redis (Docker)
REDIS_URL=redis://redis:6379/0

# Admin account
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=admin123
```

### For Local Development (With Cloudinary)
```env
# Django
SECRET_KEY=dev-key-not-secure-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Docker)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Redis (Docker)
REDIS_URL=redis://redis:6379/0

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-actual-cloud-name
CLOUDINARY_API_KEY=your-actual-api-key
CLOUDINARY_API_SECRET=your-actual-api-secret

# Admin account
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=admin123
```

### For Production (Template - Don't Use Actual Values!)
```env
# Django - CHANGE THESE!
SECRET_KEY=generate-a-secure-random-string-at-least-50-chars
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database - Use production database URL
DATABASE_URL=postgresql://user:password@db.production.com:5432/dbname

# Redis - Use production Redis URL
REDIS_URL=redis://:password@redis.production.com:6379/0

# Cloudinary - Use your real credentials
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Admin account - Change password!
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@yourdomain.com
SUPERUSER_PASSWORD=SecurePassword123!
```

---

## Troubleshooting .env Issues

### "ModuleNotFoundError" or "Import errors"
- Usually a typo in DATABASE_URL or REDIS_URL
- Check the format is correct

### "could not connect to database"
- Check `DB_HOST=postgres` (for Docker) or `DB_HOST=localhost` (for local)
- Check credentials match docker-compose.yml

### "image uploads not working"
- Cloudinary variables commented out or incorrect
- Either add valid Cloudinary credentials or accept that uploads won't work locally

### "sessions not working" or "user keeps getting logged out"
- REDIS_URL might be wrong
- Without Redis, sessions are stored in database (works but slower)
- Not a critical issue for local development

---

## Common Mistakes

❌ **Wrong**: `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres` (when using Docker)
✅ **Right**: `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres` (service name, not localhost)

❌ **Wrong**: `ALLOWED_HOSTS=localhost, 127.0.0.1` (spaces after comma)
✅ **Right**: `ALLOWED_HOSTS=localhost,127.0.0.1` (no spaces)

❌ **Wrong**: `DEBUG=true` (lowercase)
✅ **Right**: `DEBUG=True` (capitalized, Python boolean)

❌ **Wrong**: Committing .env to Git (exposes secrets!)
✅ **Right**: Use .env.example and add .env to .gitignore

---

## How Django Reads .env

1. You create `.env` file in project root
2. Django loads it at startup (via `python-dotenv`)
3. All `SECRET_KEY=value` become `os.getenv("SECRET_KEY")`
4. Missing variables fall back to defaults in `settings.py`

If a variable is missing, Django either:
- Uses a default value (if set in settings.py)
- Crashes with "key not found" error
- Works without it (if optional)

Check `settings.py` to see which variables are required vs optional.

---

## Summary

| Variable | Required | Local Dev | Production |
|----------|----------|-----------|------------|
| SECRET_KEY | Yes | Can be simple | Must be long & random |
| DEBUG | Yes | True | False |
| DATABASE_URL | Yes | Docker URL | Production URL |
| REDIS_URL | No | Docker URL | Production URL |
| CLOUDINARY_* | No | Leave blank | Add credentials |
| SUPERUSER_* | Yes | Any values | Secure password |

Start with the "Simplest" example above and expand as needed!
