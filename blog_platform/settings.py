import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from .ckeditor_config import *

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# Check if running tests early to configure appropriately
TESTING = 'test' in sys.argv

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,.railway.app,.onrender.com").split(",")

# CSRF Trusted Origins for deployment platforms
CSRF_TRUSTED_ORIGINS = [
    'https://*.up.railway.app',
    'https://*.onrender.com',
]

# Add custom CSRF origins from environment (for Coolify/custom domains)
# Format: CSRF_TRUSTED_ORIGINS_CUSTOM=https://yourdomain.com,https://www.yourdomain.com
custom_origins = os.getenv("CSRF_TRUSTED_ORIGINS_CUSTOM", "")
if custom_origins:
    CSRF_TRUSTED_ORIGINS.extend(custom_origins.split(","))

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary_storage",
    "django.contrib.staticfiles",
    "cloudinary",

    # Third party apps
    "django_ckeditor_5",
    "crispy_forms",
    "crispy_tailwind",
    "csp",
    "django_bleach",

    # Django REST Framework
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
    "django_filters",

    # Local apps
    "core",
    "accounts",
    "content",
    "engagement",
]

# Cloudinary Configuration
if TESTING:
    CLOUDINARY_STORAGE = {}
else:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
        'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    }

# Media URL (keep for compatibility)
MEDIA_URL = "/media/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

CKEDITOR_5_CUSTOM_CSS = 'css/article-content.css'

CKEDITOR_5_UPLOAD_PATH = "uploads/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# WhiteNoise Configuration for production static files
WHITENOISE_USE_FINDERS = True  # Find files from installed apps
WHITENOISE_AUTOREFRESH = DEBUG  # Auto-refresh during development

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Only enable HTTPS redirects in production, not in development
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    # Trust X-Forwarded-Proto header from Railway's proxy
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session security
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

ROOT_URLCONF = "blog_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "blog_platform.wsgi.application"

# Database
if os.getenv("DATABASE_URL"):
    # Production database configuration
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Local development database
    db_port = os.getenv("DB_PORT", "5432")
    try:
        db_port = int(db_port)
    except (ValueError, TypeError):
        db_port = 5432

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "postgres"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": db_port,
        }
    }

# Redis Configuration
REDIS_URL = os.getenv('REDIS_URL') if not TESTING else None

# Always use database sessions and dummy cache as fallback
# Redis is optional for performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

if REDIS_URL:
    print(f"[*] Redis URL found: {REDIS_URL[:30]}...")
else:
    print("[*] Redis: Skipped (using database sessions)")

CACHE_TTL = 60 * 15

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth URLs
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Set Cloudinary as default file storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Logging configuration
if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
else:
    # Simple logging for development
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        },
    }

# Use SQLite for testing and database sessions (bypass Redis connection errors)
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    # Use database sessions for tests to avoid Redis connection issues
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    # Disable Redis cache for tests
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    # Use local filesystem storage for tests instead of Cloudinary
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
    # Disable Cloudinary for tests
    CLOUDINARY_STORAGE = {}

# ============================================================================
# Django REST Framework Configuration
# ============================================================================

REST_FRAMEWORK = {
    # Authentication: Use JWT tokens for API, session auth for browsable API
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],

    # Permissions: Authenticated users can write, anyone can read
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],

    # Pagination: Return 20 items per page by default
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,

    # Filtering: Enable advanced filtering, search, and ordering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    # Schema: Use drf-spectacular for OpenAPI schema generation
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Authentication Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Short-lived access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # Long-lived refresh token
    'ROTATE_REFRESH_TOKENS': True,                     # Issue new refresh token on refresh
    'BLACKLIST_AFTER_ROTATION': False,                 # Don't use blacklist (needs extra app)
}

# API Documentation Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Blog Platform API',
    'DESCRIPTION': 'A modern content management API with articles, bulletins, and engagement features',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# CORS Settings for Frontend Development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',      # React default
    'http://localhost:5173',      # Vite default
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
]

# In production, add your frontend domain
if not DEBUG:
    production_frontend = os.getenv('FRONTEND_URL')
    if production_frontend:
        CORS_ALLOWED_ORIGINS.append(production_frontend)

# Allow credentials (cookies, authorization headers)
CORS_ALLOW_CREDENTIALS = True

print("Cloudinary storage configured")
print(f"Database: {'Production (PostgreSQL)' if os.getenv('DATABASE_URL') else 'Local Development'}")
print(f"Redis: {'Connected' if REDIS_URL else 'Not configured (using fallback)'}")
print(f"Debug Mode: {DEBUG}")