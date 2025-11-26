# Security Policy - Blog Platform

## Overview

This document outlines the security practices, vulnerabilities handled, and reporting procedures for the Blog Platform. The application is built with Django 5.2, which includes built-in security features, and we've added additional layers of protection.

---

## Security Features Implemented

### 1. Authentication & Authorization

#### User Authentication
- **Method**: Django's built-in authentication system with hashed passwords (PBKDF2)
- **Session Management**: Secure cookies with `HttpOnly` and `Secure` flags in production
- **CSRF Protection**: Django's CSRF middleware prevents cross-site request forgery attacks
- **Password Validation**: Enforced through Django's password validators (minimum length, complexity)

#### Role-Based Access Control (RBAC)
- **Three Roles**: Reader, Writer, Administrator
- **Mixins**: Custom permission mixins enforce role checks on views:
  - `ReaderRequiredMixin` - Any authenticated user
  - `WriterRequiredMixin` - Only writers
  - `AdministratorRequiredMixin` - Only admins
- **Object-Level Permissions**: `ArticleOwnerMixin` ensures writers can only edit their own articles

### 2. Input Validation & Sanitization

#### HTML Content Sanitization
- **Library**: Bleach library for HTML content filtering
- **Location**: `core/sanitization.py`
- **Implementation**: Automatic sanitization in `Article.save()` method
- **Whitelist**: Only safe tags allowed (p, br, strong, em, u, ol, ul, li, h1-h3)
- **XSS Prevention**: Removes all script tags, event handlers, and dangerous attributes

#### Form Validation
- **Server-Side**: All forms validated using Django forms API
- **Client-Side**: HTML5 validation for basic UX improvement (not security)
- **File Uploads**: Cloudinary handles file validation (MIME type, size limits)

### 3. Database Security

#### SQL Injection Prevention
- **Django ORM**: All database queries use parameterized queries via ORM
- **No Raw SQL**: Raw SQL is avoided unless absolutely necessary
- **Query Safety**: Django's query builder prevents SQL injection

#### Data Protection
- **Passwords**: Hashed using PBKDF2 (Django default)
- **Secrets**: Environment variables for all sensitive data (SECRET_KEY, API keys, DB credentials)
- **Encryption**: Django's default encryption for session data in Redis

#### Database Constraints
- **Unique Constraints**: Article visibility constraints prevent data inconsistency
- **Foreign Keys**: Cascade delete ensures referential integrity
- **Indexes**: Indexes on frequently queried fields for performance

### 4. Network Security

#### HTTPS Enforcement
- **Production**: `SECURE_SSL_REDIRECT=True` forces all traffic to HTTPS
- **Cookies**: `SESSION_COOKIE_SECURE=True` and `CSRF_COOKIE_SECURE=True`
- **HSTS**: `SECURE_HSTS_SECONDS=31536000` (1 year) prevents downgrade attacks

#### Security Headers
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-XSS-Protection**: Legacy XSS filter support
- **Referrer-Policy**: Controls referrer information
- **Content-Security-Policy**: (Optional) Can be added for stricter control

### 5. API Security

#### CSRF Tokens
- **Form Protection**: All POST forms include Django's CSRF token
- **AJAX Protection**: JavaScript requests include CSRF token in headers

#### Rate Limiting
- **Optional**: Can be enabled via django-ratelimit
- **Implementation**: Prevents brute-force attacks on login/toggles

### 6. File Upload Security

#### Cloudinary Storage
- **Security**: All uploads processed through Cloudinary API
- **Validation**: Cloudinary validates file types and sizes
- **CDN**: Content served through Cloudinary CDN with DDoS protection
- **No Local Storage**: User uploads don't touch server filesystem

#### Allowed File Types
- **Images**: JPG, PNG, GIF, WebP
- **Documents**: PDF (configurable in Cloudinary settings)

### 7. Third-Party Security

#### Dependencies
- **Django 5.2**: Latest LTS version with security patches
- **Package Updates**: Regular updates recommended via `pip install --upgrade`
- **Vulnerability Scanning**: Use `safety` or `bandit` to scan for known vulnerabilities

#### Cloudinary API
- **API Key Rotation**: Can be rotated in Cloudinary dashboard
- **API Secret**: Never exposed in client-side code
- **Signed Uploads**: Support for signed URLs for private content

---

## Vulnerability Handling

### Cross-Site Scripting (XSS)
- **Protection**: HTML sanitization on Article content saves
- **Implementation**: Bleach library removes dangerous tags/attributes
- **Testing**: Test with `<script>alert('xss')</script>` in article content

### Cross-Site Request Forgery (CSRF)
- **Protection**: Django's CSRF middleware on all POST/PUT/DELETE requests
- **Implementation**: CSRF tokens on all forms

### SQL Injection
- **Protection**: Django ORM parameterized queries
- **Implementation**: All database queries use `.filter()`, `.create()`, etc. instead of raw SQL

### Broken Authentication
- **Protection**: Password hashing with PBKDF2, secure session management
- **Implementation**: Django's authentication system with custom mixins

### Sensitive Data Exposure
- **Protection**: HTTPS only in production, secure cookies
- **Implementation**: `SECURE_SSL_REDIRECT=True`, secure flag on cookies

### Security Misconfiguration
- **Protection**: Environment-specific settings via `.env` file
- **Implementation**: `DEBUG=False` in production, secret key in environment variable

### Insecure Deserialization
- **Protection**: Django's session serializer (JSON default, not pickle)
- **Implementation**: Sessions use JSON format which is safe

### Broken Access Control
- **Protection**: Role-based mixins, object-level permissions
- **Implementation**: `WriterRequiredMixin`, `ArticleOwnerMixin`, admin-only views

### Self-Engagement Prevention
- **Protection**: Views prevent users from liking/commenting on own articles
- **Implementation**: Check `article.bulletin.profile.user != request.user` before allowing

---

## Security Checklist for Deployment

- [ ] `SECRET_KEY` is set to a random secure value (not default)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` contains only your production domains
- [ ] `SECURE_SSL_REDIRECT=True` enabled
- [ ] `SESSION_COOKIE_SECURE=True` enabled
- [ ] `CSRF_COOKIE_SECURE=True` enabled
- [ ] Database credentials in environment variables, not in code
- [ ] Cloudinary API secret in environment variables
- [ ] PostgreSQL user has limited permissions (not superuser)
- [ ] Redis (if used) behind firewall or password-protected
- [ ] Static files collected with `collectstatic`
- [ ] Database migrated with `python manage.py migrate`
- [ ] HTTPS certificate installed (Railway/Heroku provides automatically)

---

## Supported Versions

| Version | Status | Security Updates |
|---------|--------|------------------|
| 1.0.x | Current | All patches |
| < 1.0 | EOL | No updates |

---

## Reporting a Vulnerability

### Responsible Disclosure

If you discover a security vulnerability, **please do not create a public GitHub issue**. Instead:

1. **Email**: Contact project maintainer privately at `admin@blogplatform.com`
2. **Include**:
   - Detailed description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

3. **Timeline**:
   - You'll receive acknowledgment within 48 hours
   - We'll provide status update within 7 days
   - Critical vulnerabilities will be patched within 2 weeks
   - Public disclosure after patch is released (allow 30 days minimum)

### Bug Bounty
Currently, this is a learning/portfolio project without a formal bug bounty program. However, we appreciate responsible disclosure and will credit security researchers in release notes.

---

## Security Best Practices for Developers

### When Adding New Features
1. **Input Validation**: Always validate user input on the server side
2. **Authorization Checks**: Use mixins to verify user has permission
3. **Avoid Raw SQL**: Use Django ORM for all database queries
4. **Test with Malicious Input**: Try `<script>`, SQL injection, path traversal, etc.
5. **Sanitize Before Storage**: Clean HTML content before saving to database

### When Handling User Data
1. **Never Log Passwords**: Never print or store passwords
2. **Use Hashed Values**: For any sensitive data (emails in notifications, etc.)
3. **Expire Sessions**: Users should log out after inactivity
4. **Validate File Uploads**: Check MIME types and file sizes
5. **Secure Sensitive Information**: Use `@admin_required` for admin-only data

### Testing for Vulnerabilities
```bash
# Install security scanners
pip install bandit safety

# Scan Python code for security issues
bandit -r .

# Check dependencies for known vulnerabilities
safety check
```

---

## Dependency Security

### Critical Dependencies
- **Django 5.2**: Web framework with built-in security features
- **bleach**: HTML sanitization library
- **cloudinary**: Secure file storage
- **psycopg2**: PostgreSQL database adapter
- **redis**: Caching layer (optional)

### Keeping Dependencies Updated
```bash
# Check for outdated packages
pip list --outdated

# Update critical security patches
pip install --upgrade django bleach

# Generate requirements.txt with pinned versions
pip freeze > requirements.txt
```

### Monitoring
- Watch Django security releases: https://www.djangoproject.com/weblog/
- GitHub alerts for vulnerable dependencies in this repo
- Use `safety check` regularly to scan for CVEs

---

## Security Incident Response

### If a Vulnerability is Discovered
1. **Assess**: Determine severity and affected versions
2. **Notify**: Inform maintainers and key stakeholders
3. **Patch**: Create fix and test thoroughly
4. **Release**: Push security patch as soon as possible
5. **Communicate**: Notify users to upgrade

### Severity Levels
- **Critical** (CVSS 9-10): RCE, auth bypass, data exposure → Patch immediately
- **High** (CVSS 7-8): Significant impact → Patch within 2 weeks
- **Medium** (CVSS 4-6): Limited impact → Patch within 4 weeks
- **Low** (CVSS 0-3): Minimal impact → Include in next release

---

## Production Hardening

### Recommended Settings
```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "cdn.tailwindcss.com"),
    "style-src": ("'self'", "'unsafe-inline'", "cdn.tailwindcss.com"),
}
```

### Infrastructure Security
- **Web Server**: Use gunicorn + nginx (not Django dev server)
- **Database**: PostgreSQL with strong password, non-root user
- **Firewall**: Only expose ports 80 (HTTP redirect) and 443 (HTTPS)
- **Backups**: Automated daily backups with encryption
- **Monitoring**: Log all access, alert on suspicious activity

---

## Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Django Security**: https://docs.djangoproject.com/en/5.2/topics/security/
- **Bleach Documentation**: https://bleach.readthedocs.io/
- **Cloudinary Security**: https://cloudinary.com/security

---

## Questions?

For security-related questions, contact: `admin@blogplatform.com`
