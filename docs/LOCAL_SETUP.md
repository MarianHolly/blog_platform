# Local Development Setup Guide

This guide will help you run the blog platform locally with Docker and Docker Compose. No experience needed - just follow the steps!

## Prerequisites

1. **Docker Desktop** - Download from https://www.docker.com/products/docker-desktop
   - Includes both Docker and Docker Compose
   - Available for Windows, Mac, and Linux
   - After installation, restart your computer

2. **Git** (already have this since you're reading this)

3. **A code editor** (VS Code, PyCharm, etc.) - optional but helpful

## Step 1: Verify Docker Installation

Open PowerShell or Command Prompt and run:

```powershell
docker --version
docker-compose --version
```

You should see version numbers. If not, restart Docker Desktop and try again.

## Step 2: Create the .env File

In your project root directory (where `docker-compose.yml` is located), create a file named `.env` with this exact content:

```env
# Django settings
SECRET_KEY=your-secret-key-change-this-in-production-12345abcde
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL will run in Docker)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Redis (Redis will run in Docker)
REDIS_URL=redis://redis:6379/0

# Cloudinary (optional - for image uploads)
# You can skip these for now. Without them, image uploads won't work but the app will run
# CLOUDINARY_CLOUD_NAME=your-cloud-name
# CLOUDINARY_API_KEY=your-api-key
# CLOUDINARY_API_SECRET=your-api-secret

# Superuser (admin account) - will be created automatically
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@blogplatform.com
SUPERUSER_PASSWORD=admin123
```

### Important Notes:
- `postgres:5432` and `redis:6379` are the Docker internal names (not localhost!)
- Keep `DEBUG=True` for local development
- You can change the superuser password to something you prefer
- Cloudinary is optional - the app will work without it

## Step 3: Start the Application

Navigate to your project directory in PowerShell/Command Prompt and run:

```powershell
docker-compose up
```

This will:
1. Download PostgreSQL and Redis images (first time only - takes 2-3 minutes)
2. Start PostgreSQL database
3. Start Redis cache
4. Install Python dependencies
5. Run migrations automatically
6. Start the Django development server

**Wait until you see this message:**
```
blog_platform  | Starting development server at http://127.0.0.1:8000/
```

This means everything is running! Don't close this window.

## Step 4: Access Your Application

Open your web browser and go to:
- **Application**: http://localhost:8000
- **Admin Dashboard**: http://localhost:8000/admin

Login with:
- **Username**: `admin`
- **Password**: `admin123`

## Troubleshooting Common Issues

### Issue: Docker containers not starting

**Error**: "Docker daemon is not running"
- **Solution**: Start Docker Desktop from your applications

**Error**: "Port 5432 or 6379 already in use"
- **Solution**: You may have PostgreSQL or Redis running locally
  ```powershell
  docker-compose down  # Stop containers
  # Then check if you have local PostgreSQL/Redis running and stop them
  ```

### Issue: Migrations fail

**Error**: "relation does not exist"
- **Solution**: This usually fixes itself. Stop containers (Ctrl+C) and run again:
  ```powershell
  docker-compose down
  docker-compose up
  ```

### Issue: Can't upload images

- **Expected**: Without Cloudinary credentials, image uploads won't work
- **Solution**: Leave Cloudinary fields commented out for now - you can add them later

### Issue: Website is very slow or gets 500 errors

**Solution**: Look at the error messages in your terminal window where docker-compose is running. Common issues:
- Check database connection (should say "PostgreSQL connection successful")
- Check Redis connection (should say "Redis: Configured")

## Stopping and Restarting

### Stop the application
Press `Ctrl+C` in the terminal where docker-compose is running

### Start again
```powershell
docker-compose up
```

### Completely clean up (deletes database data)
```powershell
docker-compose down -v
docker-compose up
```

This removes everything and starts fresh (you'll need to recreate admin account).

## Understanding What's Running

Your docker-compose.yml defines two services:

1. **PostgreSQL Database** (Port 5432)
   - Runs in a container named `blog-platform-postgres`
   - Data saved in `postgres_data` volume (persists between restarts)
   - Connection string: `postgresql://postgres:postgres@postgres:5432/postgres`

2. **Redis Cache** (Port 6379)
   - Runs in a container named `blog-platform-redis`
   - Data saved in `redis_data` volume
   - Connection string: `redis://redis:6379/0`

3. **Django Application** (Port 8000)
   - Runs the development server
   - Automatically runs migrations on startup (from entrypoint.sh)
   - Automatically creates superuser if it doesn't exist

## Common Commands While Running

**In a separate PowerShell/Command Prompt window:**

```powershell
# Access Django shell
docker-compose exec web python manage.py shell

# Create a new migration
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Check application status
docker-compose ps

# View database
docker-compose exec postgres psql -U postgres -d postgres
# Inside psql:
# \dt  (list tables)
# \q   (quit)
```

## Next Steps After Getting It Running

1. **Test the application**: Create a writer account, write an article, test the features
2. **Explore the admin**: http://localhost:8000/admin to see the database
3. **Check logs**: Look at the terminal output for any errors
4. **Add Cloudinary** (optional): Sign up at cloudinary.com and add credentials to .env

## Notes on Deployment Issues

Since you mentioned Render was slow:
- Render's free tier has limited resources
- Docker helps because everything is containerized and consistent
- Local development with Docker is the same as production - fewer surprises
- You can test scaling locally before deploying

When you're ready to deploy elsewhere, you can:
- **Heroku** (similar to Render, easier setup)
- **Railway** (newer, faster startup)
- **DigitalOcean** (cheap VPS, full control)
- **AWS** (scalable but more complex)

All work similarly - they pull your Docker image and run it. Local testing with Docker makes deployment debugging much easier!

## Getting Help

If something isn't working:
1. Copy the error message from the terminal
2. Check the CLAUDE.md file for Django-specific commands
3. Google the error (usually it's a common issue with a known solution)
