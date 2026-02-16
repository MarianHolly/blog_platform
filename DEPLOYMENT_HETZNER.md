# Hetzner + Coolify Deployment Guide

**Detailed step-by-step guide for deploying to Hetzner Cloud with Coolify**

---

## Overview

**What you'll get**:
- VPS on Hetzner (€4.51/month)
- Coolify (open-source Heroku alternative)
- PostgreSQL database
- Redis cache
- Automatic SSL (Let's Encrypt)
- GitHub auto-deploy
- Easy monitoring

**Total setup time**: ~1.5 hours

---

## Prerequisites Checklist

- [ ] GitHub account with your repository
- [ ] Domain name (optional but recommended)
- [ ] Cloudinary account for media storage
- [ ] Credit card for Hetzner (€5-10 minimum deposit)
- [ ] SSH key generated on your machine

---

## Part 1: Hetzner Account Setup (10 min)

### Step 1: Create Hetzner Account

1. Go to https://www.hetzner.com/cloud
2. Click "Sign Up"
3. Complete registration
4. Verify email
5. Add payment method (credit card or PayPal)
6. Add €10 credit (minimum)

### Step 2: Generate SSH Key (if needed)

**On your local machine**:
```bash
# Check if you have SSH key
ls -la ~/.ssh/

# If no id_rsa.pub, generate new key
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Press Enter for default location
# Set passphrase (optional but recommended)

# Copy public key
cat ~/.ssh/id_rsa.pub
# Copy the entire output
```

---

## Part 2: Create Hetzner VPS (20 min)

### Step 1: Create New Project

1. Login to Hetzner Cloud Console
2. Click "New Project"
3. Name: `blog-platform`
4. Click "Create Project"

### Step 2: Add SSH Key to Project

1. In project, go to "Security" → "SSH Keys"
2. Click "Add SSH Key"
3. Paste your public key (from `~/.ssh/id_rsa.pub`)
4. Name: `my-laptop` (or your device name)
5. Click "Add SSH Key"

### Step 3: Create Firewall

1. Go to "Security" → "Firewalls"
2. Click "Create Firewall"
3. Name: `web-firewall`
4. **Add Inbound Rules**:
   - SSH (22) → Your IP only (or 0.0.0.0/0 if dynamic IP)
   - HTTP (80) → 0.0.0.0/0
   - HTTPS (443) → 0.0.0.0/0
   - Custom (8000) → 0.0.0.0/0 (for Coolify dashboard)
5. Click "Create Firewall"

### Step 4: Create Server

1. Click "Add Server"
2. **Location**: Nuremberg, Germany (or nearest to you)
3. **Image**: Ubuntu → 24.04
4. **Type**:
   - Shared vCPU → CPX11 (2 vCPU, 2GB RAM) - €4.51/month
   - (For production with more traffic, use CPX21 - 3 vCPU, 4GB RAM - €9.52/month)
5. **Networking**:
   - ✅ Public IPv4
   - ✅ Public IPv6
6. **SSH Keys**: Select your key
7. **Firewalls**: Select `web-firewall`
8. **Volumes**: None
9. **Name**: `blog-platform-server`
10. Click "Create & Buy Now"

**Wait 1-2 minutes for server to start**

### Step 5: Note Server IP

1. Server will appear in dashboard
2. **Copy the IPv4 address** (e.g., 95.217.123.456)
3. Save this IP - you'll need it multiple times

---

## Part 3: Install Coolify (25 min)

### Step 1: SSH into Server

**From your terminal**:
```bash
ssh root@YOUR_SERVER_IP
# Replace YOUR_SERVER_IP with actual IP

# First time you'll see:
# "The authenticity of host... Are you sure you want to continue?"
# Type: yes

# You should now be logged into the server
# Prompt will show: root@blog-platform-server:~#
```

### Step 2: Update System

```bash
# Update package lists
apt update

# Upgrade packages
apt upgrade -y

# This may take 5-10 minutes
```

### Step 3: Install Coolify

**Run the one-line installer**:
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

**This will**:
- Install Docker & Docker Compose
- Install Coolify
- Install Traefik (reverse proxy)
- Setup PostgreSQL for Coolify
- Configure automatic SSL

**Installation takes 5-10 minutes**

**You'll see output like**:
```
✓ Docker installed
✓ Docker Compose installed
✓ Coolify installed
✓ Starting services...
✓ Coolify is running!

Access Coolify at: http://YOUR_SERVER_IP:8000
```

### Step 4: Initial Coolify Setup

1. **Open browser**: `http://YOUR_SERVER_IP:8000`
2. **Registration page appears**
3. **Create admin account**:
   - Email: your-email@example.com
   - Name: Your Name
   - Password: (strong password)
4. Click "Register"
5. **You're logged into Coolify!**

---

## Part 4: Configure Domain (Optional, 15 min)

**If you have a domain (e.g., yourdomain.com)**:

### Step 1: Add DNS Records

**In your domain provider (Namecheap, GoDaddy, Cloudflare, etc.)**:

Add these A records:
```
Type: A
Name: blog (or @ for root domain)
Value: YOUR_SERVER_IP
TTL: 300 (or Auto)

Type: A
Name: api
Value: YOUR_SERVER_IP
TTL: 300
```

**Wait 5-10 minutes for DNS to propagate**

Verify with:
```bash
# On your local machine
nslookup blog.yourdomain.com
# Should show YOUR_SERVER_IP
```

### Step 2: Configure Domain in Coolify

1. In Coolify dashboard → Settings → Configuration
2. **Instance Domain**: Leave as IP for now
3. We'll configure app-specific domains later

---

## Part 5: Deploy Application (45 min)

### Step 1: Prepare Your Repository

**On your local machine**:

1. **Ensure all changes are committed**:
```bash
git status
git add .
git commit -m "Prepare for deployment"
git push origin dev
```

2. **Create production settings** (if not exists):

Create `blog_platform/settings_prod.py`:
```python
from .settings import *

DEBUG = False

# Will be set via environment variables
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Trust Coolify's proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

3. **Update Dockerfile** (if needed):

Ensure your `Dockerfile` has:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD python manage.py migrate && \
    gunicorn blog_platform.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
```

4. **Push changes**:
```bash
git add .
git commit -m "Add production configuration"
git push origin dev
```

### Step 2: Create PostgreSQL Database in Coolify

1. **In Coolify**: Click "New Resource" → "Database"
2. **Select**: PostgreSQL
3. **Configuration**:
   - Name: `blog-platform-db`
   - Version: PostgreSQL 17
   - Database Name: `blog_platform`
   - Username: `blog_user`
   - Password: (auto-generated, or set your own)
4. Click "Create"
5. **Wait 2-3 minutes** for database to start
6. **Copy connection details**:
   - Click on database → Connection Details
   - Copy the **Internal URL** (e.g., `postgresql://blog_user:password@blog-platform-db:5432/blog_platform`)
   - Save this - you'll need it for app env vars

### Step 3: Create Redis in Coolify

1. Click "New Resource" → "Database"
2. Select: Redis
3. Configuration:
   - Name: `blog-platform-redis`
   - Version: Redis 7
4. Click "Create"
5. Wait for startup
6. Copy **Internal URL** (e.g., `redis://blog-platform-redis:6379`)

### Step 4: Create Application in Coolify

1. Click "New Resource" → "Application"
2. **Source**:
   - Repository Type: Public Repository
   - Repository URL: `https://github.com/yourusername/blog_platform`
   - Branch: `dev`
3. **Build Configuration**:
   - Build Pack: Dockerfile
   - Dockerfile Location: `./Dockerfile`
4. **Domain**:
   - If you have domain: `blog.yourdomain.com`
   - If not: Leave empty (will use IP:port)
5. Click "Create Application"

### Step 5: Configure Environment Variables

**In your application page** → Environment Variables:

Click "Bulk Edit" and paste:

```bash
# Django
SECRET_KEY=your-very-long-random-secret-key-here-use-generator
DEBUG=False
DJANGO_SETTINGS_MODULE=blog_platform.settings
ALLOWED_HOSTS=blog.yourdomain.com,YOUR_SERVER_IP
CSRF_TRUSTED_ORIGINS=https://blog.yourdomain.com

# Database (use the URL from Step 2)
DATABASE_URL=postgresql://blog_user:password@blog-platform-db:5432/blog_platform

# Redis (use the URL from Step 3)
REDIS_URL=redis://blog-platform-redis:6379/0

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Superuser (for initial setup)
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@yourdomain.com
SUPERUSER_PASSWORD=your-secure-admin-password

# Email (optional, for later)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.sendgrid.net
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=apikey
# EMAIL_HOST_PASSWORD=your-sendgrid-api-key
# DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**Generate SECRET_KEY**:
```python
# On your local machine, in Python shell
python manage.py shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
# Copy the output and use as SECRET_KEY
```

Click "Save"

### Step 6: Configure Health Check

1. In application page → Health Check
2. **Health Check URL**: `/admin/` (or create dedicated `/health/` endpoint)
3. **Enabled**: Yes
4. Save

### Step 7: Deploy Application

1. **Click "Deploy" button** (top right)
2. **Watch build logs** (automatically shown)
3. **Wait 5-10 minutes** for:
   - Docker image build
   - Dependencies installation
   - Static files collection
   - Migrations
   - Server startup

**Expected logs**:
```
Building Docker image...
Installing dependencies...
Collecting static files...
Running migrations...
Starting gunicorn...
✓ Deployment successful
```

### Step 8: Verify Deployment

1. **Click on the application URL** (shown at top)
   - If domain: `https://blog.yourdomain.com`
   - If no domain: `http://YOUR_SERVER_IP:PORT`

2. **You should see your homepage!**

3. **Test admin panel**: `https://blog.yourdomain.com/admin/`
   - Login with SUPERUSER credentials
   - Should work!

4. **Test API**: `https://blog.yourdomain.com/api/v1/docs/`
   - Swagger UI should load

---

## Part 6: Post-Deployment Setup (20 min)

### Step 1: Generate Mock Data

**Option A: Via Coolify Terminal**
1. Go to application → Terminal
2. Run:
```bash
python manage.py generate_mock_data --users 50 --articles 100
```

**Option B: Via SSH**
```bash
# From your local terminal
ssh root@YOUR_SERVER_IP

# Find the application container
docker ps | grep blog-platform

# Execute command in container
docker exec -it CONTAINER_ID python manage.py generate_mock_data --users 50 --articles 100
```

### Step 2: Create Additional Superuser (Optional)

```bash
docker exec -it CONTAINER_ID python manage.py createsuperuser
```

### Step 3: Test All Features

- [ ] Homepage loads
- [ ] User registration works
- [ ] Login works
- [ ] Article creation (as writer)
- [ ] Comments work
- [ ] Likes work
- [ ] API endpoints work
- [ ] Admin panel accessible
- [ ] Static files loading
- [ ] Images uploading to Cloudinary

---

## Part 7: Continuous Deployment (15 min)

### Option A: Manual Deploy (Simple)

**When you push changes to GitHub**:
1. Go to Coolify → Your Application
2. Click "Deploy" button
3. Wait for rebuild

### Option B: Auto-Deploy on Push (Recommended)

**In Coolify**:
1. Application → Settings
2. **Auto Deploy**: Enable
3. **Branch**: `dev` (or `main`)
4. Save

**In GitHub**:
1. Repository → Settings → Webhooks
2. Add webhook:
   - Payload URL: `https://YOUR_SERVER_IP:8000/api/v1/webhooks/deploy/APPLICATION_ID`
   - Content type: `application/json`
   - Secret: (get from Coolify webhook settings)
3. Save

**Now**: Every push to `dev` branch → auto deploys!

---

## Part 8: Monitoring & Maintenance

### Monitor Application Health

**In Coolify Dashboard**:
- **Resources**: CPU, RAM, Disk usage
- **Logs**: Application logs in real-time
- **Deployments**: History of all deploys
- **Health Checks**: Automatic monitoring

**Access Logs**:
```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# View application logs
docker logs -f CONTAINER_NAME

# View database logs
docker logs blog-platform-db
```

### Database Backups

**In Coolify**:
1. Database → Backups
2. **Schedule**: Daily at 2 AM
3. **Retention**: 7 days
4. Enable

**Manual Backup**:
```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Backup database
docker exec blog-platform-db pg_dump -U blog_user blog_platform > backup_$(date +%Y%m%d).sql

# Download to local machine
scp root@YOUR_SERVER_IP:backup_*.sql ./backups/
```

### SSL Certificate Renewal

**Coolify auto-renews Let's Encrypt certificates!**

No manual action needed. Certificates renew every 60 days automatically.

### Update Application

**When you have new code**:
```bash
# Local machine
git add .
git commit -m "New feature"
git push origin dev

# If auto-deploy enabled: Done!
# If manual: Click "Deploy" in Coolify
```

---

## Troubleshooting

### Application Won't Start

**Check logs in Coolify**:
1. Application → Logs
2. Look for errors

**Common issues**:
- Missing environment variables
- Database connection failed
- Static files not collected

**Fix**:
1. Verify all env vars are set
2. Check DATABASE_URL format
3. Re-deploy

### Database Connection Error

**Error**: `could not connect to server`

**Fix**:
1. Ensure database is running (Coolify → Databases → should be green)
2. Check DATABASE_URL uses **internal** URL, not external
3. Restart application

### Static Files Not Loading

**Error**: 404 on CSS/JS files

**Fix**:
```bash
# In Coolify terminal or via SSH
docker exec -it CONTAINER_ID python manage.py collectstatic --noinput --clear
```

### Out of Memory

**Symptoms**: App crashes, slow response

**Fix**:
1. Upgrade server (Hetzner → Resize)
2. Optimize queries (check Django Debug Toolbar)
3. Add more Redis caching

### Domain Not Working

**Error**: Site not reachable at domain

**Fix**:
1. Verify DNS propagation: `nslookup blog.yourdomain.com`
2. Check domain in Coolify app settings
3. Verify SSL certificate issued (may take 10 min first time)

---

## Cost Breakdown

| Service | Monthly Cost | Notes |
|---------|--------------|-------|
| Hetzner VPS (CPX11) | €4.51 | 2 vCPU, 2GB RAM |
| Backups (20GB) | €0.40 | Optional |
| Cloudinary | Free | 25GB storage |
| Domain | ~€1/month | €10-15/year |
| **Total** | **~€5-6/month** | vs Railway €20+/month |

---

## Security Checklist

- [ ] SSH key authentication (no password)
- [ ] Firewall configured
- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY
- [ ] HTTPS enabled (SSL)
- [ ] Database password is strong
- [ ] Superuser password is strong
- [ ] ALLOWED_HOSTS set correctly
- [ ] CSRF_TRUSTED_ORIGINS set
- [ ] Database backups enabled
- [ ] Security headers configured

---

## Performance Optimization

### After Deployment

1. **Enable Redis caching** (update settings.py to use Redis)
2. **Configure CDN** for static files (Cloudinary already handles media)
3. **Add database indexes** (already done in models)
4. **Enable gzip compression** (Traefik handles this)

### Monitor Performance

**Use**:
- Google PageSpeed Insights
- GTmetrix
- Django Debug Toolbar (in development)

**Target metrics**:
- Page load: < 2 seconds
- Time to First Byte: < 600ms
- Lighthouse score: 90+

---

## Scaling Up

**When you need more resources**:

1. **Vertical Scaling** (same server, more power):
   - Hetzner → Servers → Resize
   - Choose bigger plan (CPX21, CPX31, etc.)
   - Downtime: ~2 minutes

2. **Horizontal Scaling** (multiple servers):
   - Add load balancer
   - Deploy to multiple servers
   - Use managed PostgreSQL

---

## Next Steps After Deployment

1. **Add uptime monitoring**: UptimeRobot (free)
2. **Add error tracking**: Sentry (free tier)
3. **Add analytics**: Plausible or Google Analytics
4. **Setup email**: SendGrid or Mailgun
5. **Custom domain email**: (optional) Google Workspace

---

## Support & Resources

**Hetzner**:
- Docs: https://docs.hetzner.com/
- Support: support@hetzner.com
- Status: https://status.hetzner.com/

**Coolify**:
- Docs: https://coolify.io/docs
- Discord: https://coollabs.io/discord
- GitHub: https://github.com/coollabs-io/coolify

**Django**:
- Deployment Checklist: https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

---

## Deployment Checklist Summary

### Pre-Deployment
- [ ] All changes committed and pushed
- [ ] Tests pass locally
- [ ] Environment variables documented
- [ ] Production settings configured
- [ ] Database migrations created

### Deployment
- [ ] Hetzner VPS created
- [ ] Coolify installed
- [ ] Domain DNS configured (if using)
- [ ] PostgreSQL database created
- [ ] Redis created
- [ ] Application created in Coolify
- [ ] Environment variables set
- [ ] Application deployed successfully

### Post-Deployment
- [ ] Application accessible
- [ ] Admin panel works
- [ ] API works
- [ ] Mock data generated
- [ ] SSL certificate issued
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Auto-deploy configured

### Testing
- [ ] Homepage loads
- [ ] User registration/login works
- [ ] Articles CRUD works
- [ ] Comments/likes work
- [ ] Static files load
- [ ] Media upload works
- [ ] API endpoints work
- [ ] Mobile responsive
- [ ] Cross-browser tested

**Congratulations! Your app is live! 🚀**
