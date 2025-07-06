# blog_platform/test_settings.py
from .settings import *

# Override storage for testing
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Disable S3 during testing
USE_S3 = False

# Use local media for tests
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

# Simplify password validation for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]


# Disable migrations for faster tests (optional)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()