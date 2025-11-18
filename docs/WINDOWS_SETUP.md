# Windows-Specific Setup Guide

Since you're on Windows, here are detailed instructions specifically for your system.

## Step 1: Install Docker Desktop on Windows

1. Download **Docker Desktop for Windows** from: https://www.docker.com/products/docker-desktop
2. Run the installer (you'll need admin rights)
3. During installation:
   - Enable "Use WSL 2 based engine" (this is the recommended option, already selected by default)
   - Check "Install required Windows components for WSL 2"
4. **Restart your computer** when installation finishes
5. Open PowerShell and verify:
   ```powershell
   docker --version
   docker-compose --version
   ```

## Step 2: Open Your Project in PowerShell

1. Open PowerShell
2. Navigate to your project:
   ```powershell
   cd "C:\Users\maria\Documents\GitHub\blog_platform"
   ```
3. List files to verify you're in the right place:
   ```powershell
   ls
   ```
   You should see: `docker-compose.yml`, `manage.py`, `Dockerfile`, etc.

## Step 3: Create the .env File (Windows Method)

**Option A: Using PowerShell (Recommended)**

Copy this exact command and paste it in PowerShell:

```powershell
@"
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
"@ | Out-File -Encoding utf8 .env
```

Then verify it was created:
```powershell
type .env
```

**Option B: Using Notepad (If you prefer)**

1. Right-click in the folder where `docker-compose.yml` is
2. Select "New" → "Text Document"
3. Name it `.env` (without the .txt extension - you may need to show file extensions in View settings)
4. Copy the content from `.env.example` and paste it
5. Save

**Option C: Using VS Code**

1. Open VS Code
2. Open the project folder
3. File → New File
4. Name it `.env`
5. Copy content from `.env.example`
6. Save

## Step 4: Start Everything

In PowerShell (make sure you're in the project directory):

```powershell
docker-compose up
```

**This will take 2-5 minutes the first time.** You'll see lots of text. Wait for this message:

```
blog_platform  | Starting development server at http://127.0.0.1:8000/
```

This means it's ready!

## Step 5: Test It

Open your browser and go to:
- http://localhost:8000 (the website)
- http://localhost:8000/admin (login with admin/admin123)

## Windows PowerShell Tips

If you get permission errors, try running PowerShell as Administrator:
1. Press `Win + X`
2. Select "Windows PowerShell (Admin)"
3. Run your commands

## Windows-Specific Issues

### Issue: "docker" command not found after installation

**Solution**:
1. Restart your computer (really important after Docker installation!)
2. Open a new PowerShell window
3. Try again

### Issue: WSL 2 error during installation

**Solution**:
1. Go to https://docs.microsoft.com/en-us/windows/wsl/install
2. Follow Microsoft's official WSL 2 setup guide
3. Then reinstall Docker Desktop

### Issue: Ports 5432 or 6379 already in use

**Solution A: Check if another Docker container is using them**
```powershell
docker ps
```

If you see postgres or redis containers, stop them:
```powershell
docker-compose down
```

**Solution B: Check if you have PostgreSQL/Redis installed locally**
1. Open Services (press `Win + R`, type `services.msc`)
2. Look for "PostgreSQL" or "Redis"
3. If found, right-click and select "Stop"

### Issue: "Docker daemon is not running"

**Solution**:
1. Click the Windows Start menu
2. Search for "Docker Desktop"
3. Click to launch it
4. Wait for the icon in system tray to show it's running (takes 30 seconds)
5. Try your docker command again

### Issue: Very slow startup or stuck at "Starting development server"

**Solution**:
1. Stop Docker (Ctrl+C)
2. Run:
   ```powershell
   docker-compose down
   docker volume prune
   docker-compose up
   ```
3. This clears caches and often fixes slow startup issues

### Issue: "postgresql connection refused"

**Solution 1: Wait longer**
- First startup takes time. Give it 2-3 minutes.

**Solution 2: Check logs**
```powershell
docker-compose logs postgres
```

**Solution 3: Restart everything**
```powershell
docker-compose down
docker-compose up
```

## Managing Docker on Windows

### View running containers
```powershell
docker ps
```

### View all containers (including stopped)
```powershell
docker ps -a
```

### Stop containers
```powershell
docker-compose down
```

### View logs
```powershell
docker-compose logs
```

### View only Django logs
```powershell
docker-compose logs web
```

### View only database logs
```powershell
docker-compose logs postgres
```

### Delete everything and start fresh
```powershell
docker-compose down -v
docker-compose up
```

## After Installation Works

Once you have it running, here are useful commands:

### Access Django shell
```powershell
docker-compose exec web python manage.py shell
```

### Create a new migration
```powershell
docker-compose exec web python manage.py makemigrations
```

### Run a specific test
```powershell
docker-compose exec web python manage.py test content
```

### View files in database container
```powershell
docker-compose exec postgres psql -U postgres -d postgres -c "\dt"
```

## Docker Desktop GUI (Alternative to PowerShell)

You can also manage containers using the Docker Desktop GUI:
1. Launch Docker Desktop
2. Go to "Containers" tab
3. You'll see your running containers
4. Click on "blog-platform" to see logs
5. Click the play/stop buttons to control them

This is a friendlier way if you prefer not using PowerShell!

## Next Steps

Once everything is running:
1. Create a test account at http://localhost:8000
2. Write a test article
3. Test the features
4. Check the admin panel at http://localhost:8000/admin
5. Review CLAUDE.md for development commands

## Asking for Help

If something goes wrong:
1. Take a screenshot of the error
2. Copy the full error message from PowerShell
3. Include:
   - What step you were on
   - The exact command you ran
   - The exact error message
4. Google the error (usually it's a common issue)
