import os
from pathlib import Path
from dotenv import load_dotenv
from .ckeditor_config import *

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com").split(",")

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

    # Local apps
    "accounts",
    "content",
    "engagement",
]

# Cloudinary Configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Media URL (keep for compatibility)
MEDIA_URL = "/media/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

CKEDITOR_5_CUSTOM_CSS = '/static/css/article-content.css'

CKEDITOR_5_UPLOAD_PATH = "uploads/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

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
REDIS_URL = os.getenv('REDIS_URL')

if REDIS_URL:
    print(f"🎯 Redis URL found: {REDIS_URL[:30]}...")
    try:
        # Simple Redis configuration without SSL complications
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': REDIS_URL,
            }
        }
        SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
        SESSION_CACHE_ALIAS = 'default'
        print("✅ Redis: Configured")
    except Exception as e:
        print(f"⚠️ Redis failed: {e}")
        # Fallback to database
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }
        SESSION_ENGINE = 'django.contrib.sessions.backends.db'
        print("📝 Using database sessions instead")
else:
    # No Redis - use database sessions
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    print("🎯 Redis: Skipped (using database sessions)")

CACHE_TTL = 60 * 15

WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['js', 'css']

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

print("🔧 Cloudinary storage configured")
print(f"🗄️ Database: {'Production (PostgreSQL)' if os.getenv('DATABASE_URL') else 'Local Development'}")
print(f"🎯 Redis: {'Connected' if REDIS_URL else 'Not configured (using fallback)'}")
print(f"🔒 Debug Mode: {DEBUG}")