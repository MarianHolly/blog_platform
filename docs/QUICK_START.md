# Quick Start Checklist

Copy and follow this checklist to get your blog platform running locally in 10 minutes.

## Pre-Flight Checklist

- [ ] Docker Desktop installed (https://www.docker.com/products/docker-desktop)
- [ ] Docker restarted after installation
- [ ] Verified Docker works: `docker --version` in PowerShell returns a version number

## Setup (5 minutes)

- [ ] Opened PowerShell and navigated to project: `cd "C:\Users\maria\Documents\GitHub\blog_platform"`
- [ ] Created `.env` file in project root with correct settings:
  ```
  SECRET_KEY=your-secret-key-change-this-in-production-12345abcde
  DEBUG=True
  ALLOWED_HOSTS=localhost,127.0.0.1

  DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
  DB_NAME=postgres
  DB_USER=postgres
  DB_PASSWORD=postgres
  DB_HOST=postgres
  DB_PORT=5432

  REDIS_URL=redis://redis:6379/0

  SUPERUSER_USERNAME=admin
  SUPERUSER_EMAIL=admin@blogplatform.com
  SUPERUSER_PASSWORD=admin123
  ```
- [ ] Saved `.env` file

## Starting the Application (2 minutes)

- [ ] In PowerShell, typed: `docker-compose up`
- [ ] Waited for message: "Starting development server at http://127.0.0.1:8000/"
- [ ] Did NOT close PowerShell window

## Testing (3 minutes)

- [ ] Opened browser to http://localhost:8000
- [ ] Saw the blog homepage
- [ ] Clicked "Admin" and logged in with: admin / admin123
- [ ] Created a test account (sign up as reader)
- [ ] Promoted account to "Writer" (if available in settings)
- [ ] Created a test article
- [ ] Viewed article on homepage

## Success! 🎉

Your blog platform is now running locally. Next steps:

### If you encounter errors:
1. Check WINDOWS_SETUP.md for your specific error
2. Check LOCAL_SETUP.md for general troubleshooting
3. Look at error messages in PowerShell carefully

### If everything works:
1. Read CLAUDE.md for development commands
2. Explore the admin panel at http://localhost:8000/admin
3. Create test content to understand the platform
4. Review code using the architecture guide in CLAUDE.md

### Stopping and restarting:
- Press `Ctrl+C` in PowerShell to stop
- Run `docker-compose up` again to restart

### To nuke everything and start fresh:
```powershell
docker-compose down -v
docker-compose up
```
(This deletes the database and recreates it)

## Common Commands While Running

**In a new PowerShell window** (keep docker-compose up running in another):

```powershell
# Django shell
docker-compose exec web python manage.py shell

# Create new migration
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Run tests
docker-compose exec web python manage.py test

# View running containers
docker ps

# View logs
docker-compose logs -f
```

## File References

- **WINDOWS_SETUP.md** - Detailed Windows-specific instructions and troubleshooting
- **LOCAL_SETUP.md** - General local development guide
- **CLAUDE.md** - Django development commands and architecture
- **.env.example** - Example environment variables

## Key URLs When Running

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | Main website |
| http://localhost:8000/admin | Django admin panel (admin/admin123) |
| http://localhost:5432 | PostgreSQL database (internal) |
| http://localhost:6379 | Redis cache (internal) |

## Ports Used

- **8000** - Django development server
- **5432** - PostgreSQL database
- **6379** - Redis cache

If any of these ports are already in use, check WINDOWS_SETUP.md or LOCAL_SETUP.md for solutions.

---

**Stuck?** Read the error message carefully, check the relevant guide file, then Google the error. Most Docker issues are common and have known solutions!
