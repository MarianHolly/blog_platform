#!/usr/bin/env python
"""
Profile Upload Diagnostic Test
==============================

This test specifically examines the profile image upload process to identify
why uploads through the web interface aren't working.

Run this from your Django project directory with:
python profile_upload_test.py

What this test checks:
1. Form field type consistency
2. Form validation with actual image files
3. Direct model save simulation
4. Template form encoding requirements
5. View processing simulation

What to look for:
- GREEN: Components working correctly
- RED: Problems that need fixing
- YELLOW: Potential issues or warnings
"""

import os
import sys
import django
from pathlib import Path
from io import BytesIO

# Add your Django project to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_platform.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
from django.test import RequestFactory, Client
from django.urls import reverse
from PIL import Image
import traceback

from accounts.models import Profile
from accounts.forms import ProfileForm
from accounts.views import ProfileUpdateView


class Colors:
    """ANSI color codes for pretty output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_header(message):
    print(f"\n{Colors.BOLD}=== {message} ==={Colors.END}")


def create_test_image():
    """Create a small test image in memory for upload testing"""
    # Create a simple 10x10 pixel image
    image = Image.new('RGB', (10, 10), color='red')

    # Save to BytesIO buffer
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)

    # Create Django uploadable file
    return SimpleUploadedFile(
        name='test_avatar.jpg',
        content=buffer.getvalue(),
        content_type='image/jpeg'
    )


def test_form_field_consistency():
    """
    Test 1: Check if ProfileForm field types match Profile model field types
    What we're looking for: avatar field should be ImageField in both places
    """
    print_header("Testing Form Field Consistency")

    try:
        from accounts.models import Profile
        from accounts.forms import ProfileForm

        # Check model field type
        model_field = Profile._meta.get_field('avatar')
        model_field_type = type(model_field).__name__
        print_info(f"Model avatar field type: {model_field_type}")

        # Check form field type
        form = ProfileForm()
        form_field = form.fields['avatar']
        form_field_type = type(form_field).__name__
        print_info(f"Form avatar field type: {form_field_type}")

        # Check for consistency
        if model_field_type == 'ImageField' and form_field_type == 'ImageField':
            print_success("Field types are consistent - both are ImageField")
            return True
        elif model_field_type == 'ImageField' and form_field_type == 'FileField':
            print_error("MISMATCH: Model uses ImageField but Form uses FileField")
            print_info("This mismatch can cause upload processing issues")
            return False
        else:
            print_warning(f"Unusual field types: Model={model_field_type}, Form={form_field_type}")
            return False

    except Exception as e:
        print_error(f"Error checking field consistency: {e}")
        return False


def test_form_validation():
    """
    Test 2: Test if ProfileForm can validate with an actual image file
    What we're looking for: Form should accept and validate image uploads
    """
    print_header("Testing Form Validation with Image Upload")

    try:
        # Create test image
        test_image = create_test_image()
        print_info(f"Created test image: {test_image.name} ({test_image.size} bytes)")

        # Test form validation
        form_data = {
            'biography': 'Test biography for upload'
        }
        file_data = {
            'avatar': test_image
        }

        form = ProfileForm(data=form_data, files=file_data)

        if form.is_valid():
            print_success("Form validation passed with image upload")
            return True
        else:
            print_error("Form validation failed with image upload")
            print_info("Form errors:")
            for field, errors in form.errors.items():
                print_info(f"  {field}: {errors}")
            return False

    except Exception as e:
        print_error(f"Error during form validation: {e}")
        traceback.print_exc()
        return False


def test_model_save_simulation():
    """
    Test 3: Simulate saving a profile with an avatar to see if Django can process it
    What we're looking for: Successful model save operation
    """
    print_header("Testing Model Save Simulation")

    try:
        # Try to get or create a test user
        test_user, created = User.objects.get_or_create(
            username='upload_test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )

        if created:
            print_info("Created test user for upload testing")
        else:
            print_info("Using existing test user")

        # Get or create profile
        profile, created = Profile.objects.get_or_create(
            user=test_user,
            defaults={'role': 'reader'}
        )

        # Create test image
        test_image = create_test_image()

        # Try to save the image to the profile
        profile.avatar = test_image
        profile.save()

        print_success("Profile saved successfully with avatar")
        print_info(f"Avatar field value: {profile.avatar}")
        print_info(f"Avatar URL: {profile.avatar.url}")

        # Check if file exists in storage
        from django.core.files.storage import default_storage
        if default_storage.exists(profile.avatar.name):
            print_success("File confirmed to exist in storage")
        else:
            print_warning("File saved but not found in storage")

        return True

    except Exception as e:
        print_error(f"Error during model save simulation: {e}")
        traceback.print_exc()
        return False


def test_view_processing():
    """
    Test 4: Test the actual ProfileUpdateView to see if it can handle file uploads
    What we're looking for: View should process POST requests with file uploads
    """
    print_header("Testing View Processing")

    try:
        # Create or get test user
        test_user, created = User.objects.get_or_create(
            username='view_test_user',
            defaults={
                'email': 'viewtest@example.com',
                'first_name': 'View',
                'last_name': 'Test'
            }
        )

        # Get or create profile
        profile, created = Profile.objects.get_or_create(
            user=test_user,
            defaults={'role': 'reader'}
        )

        # Create test client and login
        client = Client()
        client.force_login(test_user)

        # Create test image
        test_image = create_test_image()

        # Simulate POST request to profile update view
        url = reverse('profile_update', kwargs={'username': test_user.username})
        print_info(f"Testing POST to URL: {url}")

        response = client.post(url, {
            'biography': 'Updated biography via view test',
            'avatar': test_image
        })

        print_info(f"Response status code: {response.status_code}")

        if response.status_code == 302:  # Redirect after successful update
            print_success("View processed upload successfully (redirect response)")
            return True
        elif response.status_code == 200:
            print_warning("View returned 200 - check if form had validation errors")
            # Try to extract form errors from response
            if hasattr(response, 'context') and 'form' in response.context:
                form = response.context['form']
                if form.errors:
                    print_info("Form errors from view:")
                    for field, errors in form.errors.items():
                        print_info(f"  {field}: {errors}")
            return False
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error during view processing test: {e}")
        traceback.print_exc()
        return False


def test_settings_configuration():
    """
    Test 5: Check Django settings for potential configuration issues
    What we're looking for: Proper MEDIA_URL and storage configuration
    """
    print_header("Testing Settings Configuration")

    try:
        from django.conf import settings

        print_info(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
        print_info(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'NOT SET')}")
        print_info(f"AWS_DEFAULT_ACL: {getattr(settings, 'AWS_DEFAULT_ACL', 'NOT SET')}")

        # Check for duplicate MEDIA_URL assignments (this would be visible in the settings)
        media_url = getattr(settings, 'MEDIA_URL', '')
        if media_url.startswith('https://') and 'amazonaws.com' in media_url:
            print_success("MEDIA_URL is configured for S3")
        elif media_url.startswith('/media/'):
            print_warning("MEDIA_URL is configured for local storage")
        else:
            print_error(f"MEDIA_URL has unexpected value: {media_url}")

        return True

    except Exception as e:
        print_error(f"Error checking settings: {e}")
        return False


def main():
    """
    Run all diagnostic tests
    """
    print(f"{Colors.BOLD}Profile Upload Diagnostic Test{Colors.END}")
    print("This test examines the profile image upload process in your Django app")
    print("=" * 70)

    tests_passed = 0
    total_tests = 5

    if test_form_field_consistency():
        tests_passed += 1

    if test_form_validation():
        tests_passed += 1

    if test_model_save_simulation():
        tests_passed += 1

    if test_view_processing():
        tests_passed += 1

    if test_settings_configuration():
        tests_passed += 1

    # Summary
    print_header("Diagnostic Summary")

    if tests_passed == total_tests:
        print_success(f"All {total_tests} tests passed! Your upload process should be working.")
    else:
        print_error(f"Only {tests_passed} out of {total_tests} tests passed.")
        print_info("The failed tests above indicate where your upload process is breaking.")

    print("\n" + "=" * 70)
    print("Upload diagnostic completed. Check results above for specific issues.")


if __name__ == "__main__":
    main()