# Deployment Guide - Coolify on Hetzner

This guide walks you through deploying the blog platform to Hetzner using Coolify.

## Prerequisites

- Hetzner VPS (minimum 2GB RAM recommended)
- Coolify installed on your Hetzner server
- Domain name (optional, can use server IP)
- Cloudinary account for media storage

## Step 1: Set Up Hetzner VPS

1. **Create a VPS on Hetzner Cloud**
   - Go to https://console.hetzner.cloud/
   - Create new project
   - Create server (CX22 or higher: 2 vCPU, 4GB RAM)
   - Choose Ubuntu 24.04 LTS
   - Add SSH key
   - Create server

2. **Note your server IP address**

## Step 2: Install Coolify

SSH into your Hetzner server:
```bash
ssh root@YOUR_SERVER_IP
```

Install Coolify with one command:
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

Wait for installation to complete (~5 minutes). Once done, access Coolify:
```
http://YOUR_SERVER_IP:8000
```

## Step 3: Initial Coolify Setup

1. Create admin account
2. Create a new project (e.g., "Blog Platform")
3. Add your server as a resource

## Step 4: Deploy the Application

### 4.1 Create New Resource

1. In Coolify, click **+ New Resource**
2. Select **Public Repository**
3. Enter repository URL: `https://github.com/YOUR_USERNAME/blog_platform`
4. Select branch: `dev`
5. Click **Continue**

### 4.2 Configure Build Settings

Coolify will auto-detect the Dockerfile. If not:
- Build Pack: **Dockerfile**
- Dockerfile Location: `./Dockerfile`
- Port: **8000**

### 4.3 Set Environment Variables

Add these environment variables in Coolify:

**Required:**
```bash
# Django
SECRET_KEY=<generate-new-secret-key>
DEBUG=False
ALLOWED_HOSTS=YOUR_DOMAIN.com,YOUR_SERVER_IP

# Database (Coolify provides PostgreSQL)
DATABASE_URL=postgresql://USER:PASSWORD@postgres:5432/blog_platform

# Redis (Coolify provides Redis)
REDIS_URL=redis://redis:6379/0

# Cloudinary (get from cloudinary.com)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Superuser
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@yourdomain.com
SUPERUSER_PASSWORD=<strong-password>
```

**Optional (for production):**
```bash
# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email (if needed)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4.4 Add Database (PostgreSQL)

1. In Coolify, go to your project
2. Click **+ New Database**
3. Select **PostgreSQL 17**
4. Create database
5. Copy the connection URL to `DATABASE_URL` environment variable

### 4.5 Add Redis

1. In Coolify, click **+ New Database**
2. Select **Redis 7**
3. Create Redis instance
4. Copy the connection URL to `REDIS_URL` environment variable

## Step 5: Deploy

1. Click **Deploy** in Coolify
2. Wait for build to complete (~5 minutes)
3. Coolify will:
   - Build Docker image
   - Run migrations
   - Collect static files
   - Start gunicorn server

## Step 6: Configure Domain (Optional)

If you have a domain:

1. In your DNS provider, add A record:
   ```
   A record: @ -> YOUR_SERVER_IP
   A record: www -> YOUR_SERVER_IP
   ```

2. In Coolify:
   - Go to your application settings
   - Add domain: `yourdomain.com`
   - Enable **Auto-generate SSL** (Let's Encrypt)
   - Update `ALLOWED_HOSTS` environment variable to include your domain

## Step 7: Post-Deployment

### Create Superuser (if auto-creation didn't work)
```bash
# SSH into Coolify container
docker exec -it <container-name> bash

# Create superuser manually
python manage.py createsuperuser
```

### Generate Mock Data
```bash
# SSH into Coolify container
docker exec -it <container-name> bash

# Generate sample content
python manage.py generate_mock_data --users 50 --articles 100
```

### Access Admin Panel
```
https://yourdomain.com/admin
```

## Monitoring and Logs

In Coolify:
- **Logs**: View real-time application logs
- **Metrics**: Monitor CPU, memory, disk usage
- **Restart**: Restart application if needed

## Troubleshooting

### Application won't start
- Check environment variables are set correctly
- View logs in Coolify
- Ensure DATABASE_URL and REDIS_URL are correct

### Static files not loading
- Verify `collectstatic` ran successfully in logs
- Check `ALLOWED_HOSTS` includes your domain/IP

### Database connection errors
- Ensure PostgreSQL database is running in Coolify
- Verify DATABASE_URL format: `postgresql://user:password@host:port/dbname`

### SSL certificate issues
- Wait up to 5 minutes for Let's Encrypt
- Ensure DNS A record points to correct IP
- Check domain is accessible via HTTP first

## Updates and Maintenance

### Deploy updates
1. Push changes to GitHub dev branch
2. In Coolify, click **Redeploy**
3. Coolify will pull latest code and rebuild

### Database backups
- Coolify auto-backs up databases
- Configure backup schedule in database settings

### Monitor performance
- Check Coolify metrics regularly
- Scale server if needed (upgrade VPS plan)

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] Strong superuser password
- [ ] SSL/HTTPS enabled
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] Cloudinary credentials secured
- [ ] Database password strong and unique
- [ ] Regular backups enabled

## Cost Estimate (Hetzner)

- **CX22 VPS**: €5.83/month (2 vCPU, 4GB RAM) - Minimum
- **CX32 VPS**: €11.66/month (4 vCPU, 8GB RAM) - Recommended
- **Cloudinary**: Free tier (up to 25GB storage)

## Support

- Coolify Docs: https://coolify.io/docs
- Hetzner Docs: https://docs.hetzner.com/
- GitHub Issues: [your-repo]/issues
