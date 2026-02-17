# Pre-Deployment Checklist

Use this checklist before deploying to production.

## Code Ready

- [ ] All tests passing (`python manage.py test`)
- [ ] No sensitive data in code (API keys, passwords)
- [ ] `.gitignore` includes `.env`, `venv/`, `media/`
- [ ] Latest changes committed to `dev` branch
- [ ] Code pushed to GitHub

## Environment Configuration

- [ ] New `SECRET_KEY` generated for production
- [ ] `DEBUG=False` confirmed
- [ ] `ALLOWED_HOSTS` configured with domain/IP
- [ ] Cloudinary account created (free tier OK)
- [ ] Strong superuser password set

## Hetzner & Coolify Setup

- [ ] Hetzner VPS created (CX22 minimum)
- [ ] Server IP noted
- [ ] SSH access working
- [ ] Coolify installed and accessible
- [ ] Admin account created in Coolify

## Database & Services

- [ ] PostgreSQL database created in Coolify
- [ ] Redis instance created in Coolify
- [ ] `DATABASE_URL` copied from Coolify
- [ ] `REDIS_URL` copied from Coolify

## Application Deployment

- [ ] Repository connected to Coolify
- [ ] Branch set to `dev`
- [ ] All environment variables added in Coolify
- [ ] Build settings verified (Dockerfile, port 8000)
- [ ] First deployment successful

## Domain & SSL (Optional)

- [ ] Domain DNS A record points to server IP
- [ ] Domain added in Coolify
- [ ] SSL certificate generated (Let's Encrypt)
- [ ] HTTPS working
- [ ] `ALLOWED_HOSTS` includes domain
- [ ] `CSRF_TRUSTED_ORIGINS_CUSTOM` set if needed

## Post-Deployment

- [ ] Application loads at URL
- [ ] Admin panel accessible (`/admin`)
- [ ] Can log in with superuser
- [ ] Static files loading correctly
- [ ] Can create test article
- [ ] Media upload works (Cloudinary)
- [ ] Mock data generated (optional)

## Security

- [ ] `DEBUG=False` (double-check!)
- [ ] Strong `SECRET_KEY` used
- [ ] Strong database password
- [ ] Strong superuser password
- [ ] SSL/HTTPS enabled
- [ ] Firewall configured on Hetzner
- [ ] Only necessary ports open (80, 443, 22)

## Monitoring

- [ ] Coolify logs accessible
- [ ] Error logging working
- [ ] Metrics visible in Coolify
- [ ] Backup schedule configured

## Quick Commands for Post-Deployment

### View logs
```bash
# In Coolify UI: Go to Application > Logs
```

### Generate mock data
```bash
# SSH into Coolify container
docker exec -it <container-name> bash
python manage.py generate_mock_data --users 50 --articles 100
```

### Create additional superuser
```bash
docker exec -it <container-name> bash
python manage.py createsuperuser
```

### Run migrations manually (if needed)
```bash
docker exec -it <container-name> bash
python manage.py migrate
```

## Rollback Plan

If deployment fails:

1. **In Coolify**: Click "Restart" to try again
2. **Check logs**: Review deployment logs for errors
3. **Verify env vars**: Ensure all required variables are set
4. **Database issues**: Recreate PostgreSQL database if needed
5. **Contact support**: Coolify Discord or GitHub issues

## Success Criteria

✅ Application accessible via URL
✅ HTTPS working (if domain configured)
✅ Admin login successful
✅ Can create and view articles
✅ Media uploads working
✅ No errors in logs

## Next Steps After Deployment

1. Test all features thoroughly
2. Generate mock content for demo
3. Share URL with stakeholders
4. Monitor performance for first 24 hours
5. Set up regular backups
6. Document any issues encountered

---

**Last Updated**: Pre-deployment
**Deployment Date**: _____________
**Deployed By**: _____________
**Production URL**: _____________
