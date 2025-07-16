from django.apps import AppConfig
from django.conf import settings


class StorageConfig(AppConfig):
    name = 'blog_platform'

    def ready(self):
        # Force Cloudinary storage when app is ready
        settings.DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

        # Clear default storage cache
        from django.core.files.storage import default_storage
        if hasattr(default_storage, '_wrapped'):
            default_storage._wrapped = None

        print("✅ Forced Cloudinary storage in app ready()")