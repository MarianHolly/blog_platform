# Getting Started: Blog Platform Local Setup

Welcome! This guide will help you get the blog platform running on your Windows machine. Don't worry if you're new to Docker - just follow the steps.

## What You're About to Do

You're going to:
1. Install Docker (handles database, cache, and app in isolated containers)
2. Create a `.env` file (configuration)
3. Run `docker-compose up` (starts everything)
4. Test it in your browser

**Total time: 10-15 minutes** (first time takes longer due to downloading Docker images)

---

## The Simple Version (For the Impatient)

### Step 1: Install Docker Desktop
- Download: https://www.docker.com/products/docker-desktop
- Install it (keep default options)
- Restart your computer
- Verify in PowerShell: `docker --version` (should show a version)

### Step 2: Create `.env` File
In your project folder, create a file named `.env` with this content:

```env
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

**To create the file:**
- Open Notepad
- Paste the above content
- File → Save As
- Name: `.env` (just that - include the dot)
- Location: Your project root (where `docker-compose.yml` is)
- Encoding: UTF-8

### Step 3: Start It
Open PowerShell, go to your project folder, and run:

```powershell
docker-compose up
```

Wait for this message:
```
blog_platform-web  | Starting development server at http://127.0.0.1:8000/
```

### Step 4: Test It
- Browser: http://localhost:8000
- Admin: http://localhost:8000/admin (login: admin/admin123)

**Done!** You have a running blog platform.

---

## If You Get Stuck

### PowerShell: "docker command not found"
- Restart your computer (really!)
- Restart Docker Desktop
- Open a new PowerShell window

### Docker: "Port 5432 already in use"
```powershell
docker-compose down
# Then try again
docker-compose up
```

### Django: "Could not connect to database"
- Wait 30 seconds longer (database takes time to start)
- Check that `.env` has correct DATABASE_URL
- Run: `docker-compose logs postgres` to see database logs

### Website: "Connection refused"
- Make sure `docker-compose up` is still running (don't close PowerShell)
- Wait 2-3 minutes on first start (it's downloading Docker images)
- Check it's on http://localhost:8000 (not localhost:8080 or something else)

### It's taking forever
- First time startup takes 5-10 minutes
- Patience! It's downloading PostgreSQL, Redis, and Python packages
- Don't close the PowerShell window

---

## What Each Part Does

| Part | Purpose |
|------|---------|
| **Dockerfile** | Instructions to build the Django app container |
| **docker-compose.yml** | Configuration for running 3 services together (web, database, cache) |
| **.env** | Secret settings (passwords, API keys, etc.) |
| **web service** | Your Django application running on port 8000 |
| **postgres service** | Database on port 5432 (inside Docker, not visible unless you connect) |
| **redis service** | Cache/session storage on port 6379 (inside Docker) |

---

## Detailed Guides

For more detailed information, see:
- **WINDOWS_SETUP.md** - Windows-specific detailed setup and troubleshooting
- **LOCAL_SETUP.md** - General local development guide with advanced topics
- **QUICK_START.md** - Checklist-based quick reference
- **CLAUDE.md** - Django development commands and architecture

---

## Common Commands

### Start everything
```powershell
docker-compose up
```

### Stop everything (Ctrl+C works too)
```powershell
docker-compose down
```

### View logs
```powershell
docker-compose logs -f
```

### Run Django commands (in new PowerShell window while docker-compose up is running)
```powershell
# Django shell
docker-compose exec web python manage.py shell

# Create migration
docker-compose exec web python manage.py makemigrations

# Apply migration
docker-compose exec web python manage.py migrate

# Run tests
docker-compose exec web python manage.py test
```

### Clean everything and start fresh
```powershell
docker-compose down -v
docker-compose up
```

---

## Testing the Application

Once it's running:

1. **Create an account**
   - Go to http://localhost:8000
   - Click "Sign Up"
   - Create a reader account

2. **Test as writer**
   - In Django admin (http://localhost:8000/admin, login: admin/admin123)
   - Find your user, edit profile, change role to "writer"
   - Go back to website, write an article

3. **Test articles**
   - Publish an article
   - Go home, see it listed
   - Click it to view
   - Like it, comment, bookmark it

4. **Test admin features**
   - Login as admin at /admin
   - Go to Articles
   - Review the content, test approval/rejection

---

## Next Steps After It Works

1. **Explore the code**
   - See CLAUDE.md for architecture guide
   - Files to understand first:
     - `accounts/models.py` - User roles system
     - `content/models.py` - Article/Bulletin structure
     - `blog_platform/settings.py` - Configuration

2. **Make changes**
   - Edit Python files in your editor
   - Django automatically reloads changes (watch the terminal)
   - No need to restart docker-compose

3. **Add Cloudinary** (optional)
   - Sign up: https://cloudinary.com
   - Get credentials
   - Add to .env file:
     ```
     CLOUDINARY_CLOUD_NAME=your-name
     CLOUDINARY_API_KEY=your-key
     CLOUDINARY_API_SECRET=your-secret
     ```
   - Restart: `docker-compose down && docker-compose up`

4. **Run tests**
   ```powershell
   docker-compose exec web python manage.py test
   ```

---

## Understanding Why Docker

You asked about deployment issues on Render. Here's why Docker helps:

1. **Same everywhere** - Local Docker = Production Docker. No "works on my machine" problems.
2. **All-in-one** - Database, cache, app all run together, same as production.
3. **Easy testing** - Test deployment locally before pushing to Render/Railway/etc.
4. **Scaling** - When ready, Docker containers are easy to scale up.
5. **Consistency** - Everyone on your team runs identical environments.

---

## When Ready to Deploy

Once this works locally, deployment to other platforms is much easier:
- Render, Railway, Heroku, AWS, etc. all use Docker
- You can deploy with confidence knowing it works locally
- Your local tests help catch production issues before they happen

---

## Questions or Issues?

1. **Read the error message carefully** - It usually tells you what's wrong
2. **Check the relevant guide**:
   - WINDOWS_SETUP.md - Windows-specific issues
   - LOCAL_SETUP.md - General Docker issues
   - QUICK_START.md - Fast reference
3. **Google the error** - Most Docker issues have solutions online
4. **Check Docker logs** - `docker-compose logs` shows what each service is doing

---

## You've Got This! 🚀

Docker seems intimidating but you're really just:
1. Installing Docker
2. Creating a config file (.env)
3. Running one command: `docker-compose up`
4. Opening a browser

That's it. The rest happens automatically. Start with "The Simple Version" above and work your way through. You'll have it running in 15 minutes.

Happy blogging!
