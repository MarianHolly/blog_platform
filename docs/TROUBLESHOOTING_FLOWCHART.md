# Troubleshooting Flowchart

Use this when something isn't working. Follow the questions to find your problem and solution.

---

## START: Something Isn't Working

```
Do you see ANY error messages?
│
├─ YES → Go to: ERROR MESSAGES SECTION (see below)
│
└─ NO → Go to: SYMPTOMS SECTION (see below)
```

---

## ERROR MESSAGES SECTION

### "Docker command not found"
```
Did you restart your computer after installing Docker?
│
├─ NO → Restart now, then try again
│
└─ YES →
    Does "docker --version" work now?
    │
    ├─ YES → Continue with setup
    │
    └─ NO → Reinstall Docker Desktop
            Download from https://docker.com/download
```

### "Build failed" or "Error building image"
```
Read the full error message.
│
Is it about: "no space left on device"?
│
├─ YES → Your disk is full
         │ Delete unused files or uninstall old Docker images
         │ docker system prune -a
         │
├─ NO → Is it about: "permission denied"?
         │
         └─ YES → Run PowerShell as Administrator
                  Right-click PowerShell → "Run as administrator"
                  │
         │
         └─ NO → Copy the error message
                 Google it (usually has solutions)
```

### "Cannot find .env"
```
Did you create the .env file?
│
├─ NO → Create it now in your project root
        (Same folder as docker-compose.yml)
        │
└─ YES → Is the filename exactly ".env" (with the dot)?
         │
         ├─ NO → Rename it to ".env" (no .txt extension)
         │
         └─ YES → Is it in the right location?
                  Run: ls .env
                  Should show the file
                  │
                  ├─ Shows the file → Continue
                  │
                  └─ Doesn't show → Move file to project root
```

### "could not translate host name "postgres" to address"
```
This means Django can't find the database container.
│
Is docker-compose still running?
(Check the PowerShell window where you ran: docker-compose up)
│
├─ NO → Start it again: docker-compose up
│
└─ YES → Are all containers running?
         Run (in new PowerShell): docker ps
         │
         You should see 3 containers: web, postgres, redis
         │
         ├─ Only see 1 or 2 → Something failed to start
         │                   Check: docker-compose logs
         │                   Look for errors
         │
         └─ All 3 showing → Wait 30 more seconds
                             Database is slow to start
                             Try again
```

### "could not connect to server: Connection refused"
```
Is the database container running?
│
docker ps
│
├─ postgres container listed?
   │
   ├─ YES → Database is running
   │        │ It's slow to start on first run
   │        │ Wait 2-3 minutes
   │        │
   │        │ Try again: docker-compose logs postgres
   │        │ Look for: "database system is ready"
   │        │
   │
   └─ NO → Database didn't start
           Check: docker-compose logs postgres
           Look for error messages
           │
           Try: docker-compose down
               docker-compose up
               (Fresh start usually fixes it)
```

### "ValueError: invalid literal for int() with base 10"
```
This is usually about environment variables.
│
Check your .env file:
│
├─ Is DEBUG=True (not "true" or "TRUE")?
│
├─ Is DB_PORT=5432 (a number, not quoted)?
│
├─ Are there spaces after commas in ALLOWED_HOSTS?
   (Should be: localhost,127.0.0.1 NOT localhost, 127.0.0.1)
│
└─ Fix any issues and run: docker-compose down && docker-compose up
```

### "UNIQUE constraint failed"
```
This usually happens with migrations.
│
Do you have old data that conflicts?
│
Try: docker-compose down -v
     docker-compose up

This deletes everything and starts fresh.
Don't do this if you need the data!

If you need the data:
  - Try to understand the constraint error
  - Look at the table schema
  - Might need a custom migration fix
```

### "relation "accounts_profile" does not exist"
```
This means a table doesn't exist.
│
Did migrations run?
│
Check: docker-compose logs web
Look for: "Running migrations..."
         "Applying accounts.0001_initial..."
         "Operations to perform: X"
│
├─ Do you see migration messages?
   │
   ├─ YES → Migrations ran
   │        │ But something still failed
   │        │ Check for errors above migration messages
   │        │
   │
   └─ NO → Migrations didn't run
            Try: docker-compose down -v
                docker-compose up
                (Gives migrations fresh start)
```

---

## SYMPTOMS SECTION

### Website Won't Load (http://localhost:8000 shows "Connection refused")

```
Step 1: Is docker-compose running?
│
Check the PowerShell window where you ran: docker-compose up
│
├─ Window closed or shows "Gracefully stopping"?
   │ → Run again: docker-compose up
   │
└─ Window shows "Starting development server..."?
    → Continue to Step 2

Step 2: Are all 3 containers running?
│
Run (in new PowerShell): docker ps
│
You should see:
  - blog-platform-web
  - blog-platform-postgres
  - blog-platform-redis
│
├─ Missing some? → Some service failed
                   Check: docker-compose logs
                   Look for error messages
                   Try: docker-compose down && docker-compose up
                   │
│
└─ All 3 present? → Continue to Step 3

Step 3: Give it time
│
First startup takes 2-5 minutes while Docker:
  - Downloads images
  - Builds containers
  - Installs Python packages
  - Runs migrations
│
Wait 3 minutes, then try again.

Still not working?
│
Check logs: docker-compose logs web
Look for errors or "Starting development server"
```

### Can't Login (Admin Password Doesn't Work)

```
Did you set SUPERUSER_PASSWORD in .env before first startup?
│
├─ YES → Did you start docker-compose AFTER setting it?
│        │
│        ├─ NO → You have to delete database and restart
│               docker-compose down -v
│               docker-compose up
│               (Fresh start with new password)
│               │
│        └─ YES → Try the password you set
│
                  Still doesn't work?
                  │
                  Maybe you typo'd it. Try again carefully.
                  │
                  If really stuck:
                  docker-compose down -v
                  docker-compose up
                  (Sets new password: admin123)
                  │
│
└─ NO → You didn't set it, so it's the default:
        │
        Username: admin
        Password: admin123
        │
        Try these credentials
```

### Can't Upload Images

```
Are Cloudinary variables in .env?
│
├─ NO → Not needed for local dev
        │ Just skip image uploads for now
        │ You can add them later
        │
└─ YES → Did you set the variables correctly?
         │
         Check: CLOUDINARY_CLOUD_NAME
               CLOUDINARY_API_KEY
               CLOUDINARY_API_SECRET
         │
         Are they not empty? (not blank, not commented out)
         │
         ├─ NO → Add your credentials from cloudinary.com
                 docker-compose down
                 docker-compose up
                 │
         └─ YES → Did you restart docker-compose after adding them?
                  │
                  ├─ NO → Restart: docker-compose down && docker-compose up
                  │
                  └─ YES → Cloudinary config might be wrong
                           Check spelling of credentials
                           Verify on cloudinary.com they're correct
```

### Website is Very Slow

```
Are you on first startup?
│
├─ YES → Normal! Docker is downloading images
         This takes 2-5 minutes first time
         Be patient
         │
└─ NO → Website was fast before?
        │
        Could be several things:
        │
        ├─ Redis not connected (no caching)
        │  Check: docker-compose logs
        │  Look for: "Redis: Configured" or "Redis failed"
        │  │
        │
        ├─ Database slow
        │  Check: docker-compose logs postgres
        │  Look for: "database system is ready"
        │  │
        │
        ├─ Your computer is busy
        │  Check: Task Manager → Performance
        │  If CPU/RAM high, close other apps
        │  │
        │
        └─ Docker resources limited
           Right-click Docker → Settings → Resources
           Increase CPU/RAM if possible
```

### Getting "Permission Denied" Errors

```
Are you running PowerShell as Administrator?
│
├─ NO → Right-click PowerShell
        Select: "Run as administrator"
        Try again
        │
└─ YES → Try running: docker-compose down
         Then: docker-compose up

         Still doesn't work?
         │
         Might be a file permissions issue.
         Try restarting your computer.
```

### Changes to Code Aren't Showing Up

```
Did you save the file?
│
├─ NO → Save it first (Ctrl+S)
        Django should auto-reload
        │
└─ YES → Did Django reload automatically?
         │
         Check: docker-compose logs web
         Look for: "Watching for file changes..."
                   "Reload ..."
         │
         ├─ YES → Reload worked
                  │ But maybe you're looking at cached page
                  │ Try: Hard refresh (Ctrl+F5) or clear browser cache
                  │
         │
         └─ NO → Django didn't auto-reload
                 │ This can happen with certain files
                 │ Try: docker-compose down && docker-compose up
                 │
```

### Database Shows Old Data (Want Fresh Database)

```
You want to delete everything and start over?
│
Run:
  docker-compose down -v
  docker-compose up

The -v flag deletes all volumes (database data).
│
Everything will be fresh:
  - Database is empty
  - Admin account recreated
  - All tables recreated
  - Ready to start over

This takes 3-5 minutes first time.
```

### Port Already in Use

```
Error: "Port 5432 in use" or "Port 6379 in use" or "Port 8000 in use"
│
Your port is used by something else. Options:
│
Option 1: Stop other thing using the port
│
  Check what's using port 5432 (database):
    netstat -ano | findstr :5432

  If PostgreSQL running locally:
    Services (Win+R → services.msc)
    Find "PostgreSQL"
    Right-click → Stop

  Then: docker-compose down && docker-compose up
│
Option 2: Use different port in docker-compose.yml
│
  Change: "5432:5432"  →  "5433:5432"
  (You'll need to restart. More advanced.)
```

---

## DECISION TREE: QUICK REFERENCE

```
Is docker-compose running?
├─ NO → Run: docker-compose up
│
├─ ERROR in startup?
│  ├─ Docker error → See ERROR MESSAGES SECTION
│  └─ Django error → See ERROR MESSAGES SECTION
│
└─ Running, but site doesn't load?
   ├─ Can't reach http://localhost:8000 → Website Won't Load above
   ├─ Can reach, but get Django error → Check docker-compose logs
   ├─ Can reach, page is slow → Check Symptoms: Website Slow
   └─ Can reach, but wrong content → Check Code Changes section
```

---

## NUCLEAR OPTIONS (If Really Stuck)

### Option 1: Start Completely Fresh
```powershell
docker-compose down -v
docker-compose up
```
- Deletes database: ✓
- Deletes cache: ✓
- Deletes all data: ✓
- Restarts everything: ✓

### Option 2: Remove All Docker
```powershell
docker-compose down -v
docker system prune -a
docker-compose up
```
- Removes unused images: ✓
- Removes unused containers: ✓
- Deletes ALL data: ✓
- Rebuilds from scratch: ✓

### Option 3: Full Restart
```powershell
docker-compose down -v
# Close Docker Desktop
# Restart computer
# Start Docker Desktop
docker-compose up
```
- Frees all resources: ✓
- Clears memory: ✓
- Fresh start: ✓

---

## Get Help

If none of this works:

1. **Copy the FULL error message** - Not just one line
2. **Check docker-compose logs** - `docker-compose logs`
3. **Google the error** - Error messages usually have solutions online
4. **Read relevant guide**:
   - WINDOWS_SETUP.md (Windows-specific)
   - LOCAL_SETUP.md (general issues)
   - ENV_REFERENCE.md (.env issues)

Remember: Most Docker issues are common. Someone has probably had your issue before, and there's likely a solution online.

---

## Still Not Working?

Before you give up:

1. ✓ Read the error message carefully
2. ✓ Check docker-compose logs
3. ✓ Try: docker-compose down -v && docker-compose up
4. ✓ Restart your computer
5. ✓ Search the error online
6. ✓ Check all .env variables are correct
7. ✓ Ask for help (with the full error message)

You can do this! 🚀
