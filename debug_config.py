#!/usr/bin/env python
"""
Configuration Debug Script
==========================
This script will help us understand exactly what Django sees in your configuration.
"""

import os
import sys
import django
from pathlib import Path

# Add your Django project to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_platform.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage


def debug_environment():
    """Check if all environment variables are properly loaded"""
    print("=== Environment Variables ===")
    env_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_REGION_NAME',
        'AWS_S3_CUSTOM_DOMAIN'
    ]

    all_set = True
    for var in env_vars:
        value = os.environ.get(var)
        if var == 'AWS_SECRET_ACCESS_KEY' and value:
            print(f"{var}: {'*' * min(len(value), 20)} (hidden)")
        elif value:
            print(f"{var}: {value}")
        else:
            print(f"{var}: NOT SET")
            if var != 'AWS_S3_CUSTOM_DOMAIN':  # This one is optional
                all_set = False

    return all_set


def debug_django_settings():
    """Check what Django actually sees in settings"""
    print("\n=== Django Settings ===")
    print(f"USE_S3 (calculated): {getattr(settings, 'USE_S3', 'NOT SET')}")
    print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
    print(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'NOT SET')}")
    print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'NOT SET')}")
    print(f"AWS_DEFAULT_ACL: {getattr(settings, 'AWS_DEFAULT_ACL', 'NOT SET')}")


def debug_storage_backend():
    """Check what storage backend Django is actually using"""
    print("\n=== Storage Backend ===")
    print(f"Default storage class: {default_storage.__class__}")
    print(f"Default storage module: {default_storage.__class__.__module__}")

    # Try to access storage properties
    try:
        if hasattr(default_storage, 'bucket_name'):
            print(f"S3 Bucket name: {default_storage.bucket_name}")
        if hasattr(default_storage, 'location'):
            print(f"Storage location: {default_storage.location}")
    except Exception as e:
        print(f"Error accessing storage properties: {e}")


def test_storage_functionality():
    """Test if the storage backend can actually save files"""
    print("\n=== Storage Functionality Test ===")
    try:
        from django.core.files.base import ContentFile

        # Create a test file
        test_content = ContentFile(b'This is a test file for storage debugging')
        test_filename = 'debug_test_file.txt'

        print(f"Attempting to save test file: {test_filename}")

        # Try to save the file
        saved_path = default_storage.save(test_filename, test_content)
        print(f"File saved successfully to: {saved_path}")

        # Try to get the URL
        file_url = default_storage.url(saved_path)
        print(f"File URL: {file_url}")

        # Check if file exists
        if default_storage.exists(saved_path):
            print("File exists in storage: YES")
        else:
            print("File exists in storage: NO")

        # Clean up
        default_storage.delete(saved_path)
        print("Test file deleted successfully")

        return True

    except Exception as e:
        print(f"Storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Django Storage Configuration Debug")
    print("=" * 50)

    env_ok = debug_environment()
    debug_django_settings()
    debug_storage_backend()
    storage_ok = test_storage_functionality()

    print("\n=== Summary ===")
    if env_ok and storage_ok:
        print("✓ Configuration appears to be working correctly")
    else:
        print("✗ Configuration issues detected")
        if not env_ok:
            print("  - Environment variables missing or incorrect")
        if not storage_ok:
            print("  - Storage backend not functioning properly")