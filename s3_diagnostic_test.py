#!/usr/bin/env python
"""
S3 Integration Diagnostic Test
==============================

This script will systematically test your Django S3 integration to identify exactly
where problems are occurring. Run this from your Django project directory with:

python s3_diagnostic_test.py

What this test checks:
1. Environment variable loading
2. Django settings configuration
3. AWS credentials validity
4. S3 bucket connectivity
5. File upload capabilities
6. Permission setting abilities
7. URL generation correctness

What to look for in the results:
- GREEN messages indicate working components
- RED messages indicate problems that need fixing
- YELLOW messages indicate warnings or partial issues
"""

import os
import sys
import django
from pathlib import Path

# Add your Django project to the Python path
# Adjust this path if your manage.py is in a different location
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_platform.settings')
django.setup()

import boto3
import traceback
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError


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


def test_environment_variables():
    """
    Test 1: Check if environment variables are loaded correctly
    What we're looking for: All required AWS variables should be present and non-empty
    """
    print_header("Testing Environment Variables")

    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_REGION_NAME',
        'AWS_S3_CUSTOM_DOMAIN'
    ]

    all_vars_present = True

    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if var == 'AWS_SECRET_ACCESS_KEY':
                print_success(f"{var}: {'*' * min(len(value), 20)} (hidden for security)")
            else:
                print_success(f"{var}: {value}")
        else:
            print_error(f"{var}: NOT SET")
            all_vars_present = False

    if all_vars_present:
        print_success("All environment variables are loaded correctly")
    else:
        print_error("Some environment variables are missing - check your .env file")

    return all_vars_present


def test_django_settings():
    """
    Test 2: Check if Django settings are configured correctly
    What we're looking for: Django should have all AWS settings loaded from environment
    """
    print_header("Testing Django Settings Configuration")

    try:
        print_info(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
        print_info(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'NOT SET')}")
        print_info(f"AWS_S3_REGION_NAME: {getattr(settings, 'AWS_S3_REGION_NAME', 'NOT SET')}")
        print_info(f"AWS_DEFAULT_ACL: {getattr(settings, 'AWS_DEFAULT_ACL', 'NOT SET')}")
        print_info(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'NOT SET')}")

        # Check if we're using S3 storage
        if hasattr(settings, 'DEFAULT_FILE_STORAGE') and 's3' in settings.DEFAULT_FILE_STORAGE.lower():
            print_success("Django is configured to use S3 storage")
        else:
            print_error("Django is NOT configured to use S3 storage")
            return False

        print_success("Django settings appear to be configured correctly")
        return True

    except Exception as e:
        print_error(f"Error reading Django settings: {e}")
        return False


def test_aws_credentials():
    """
    Test 3: Check if AWS credentials are valid and working
    What we're looking for: Successful authentication with AWS services
    """
    print_header("Testing AWS Credentials")

    try:
        # Create a boto3 session with the credentials
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # Try to get the caller identity (this tests if credentials work)
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()

        print_success(f"AWS credentials are valid")
        print_info(f"Account ID: {identity.get('Account')}")
        print_info(f"User ARN: {identity.get('Arn')}")

        return True

    except NoCredentialsError:
        print_error("AWS credentials not found or not properly configured")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidUserID.NotFound':
            print_error("AWS Access Key ID not found")
        elif error_code == 'SignatureDoesNotMatch':
            print_error("AWS Secret Access Key is incorrect")
        else:
            print_error(f"AWS credential error: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error testing credentials: {e}")
        return False


def test_s3_bucket_access():
    """
    Test 4: Check if we can access the specific S3 bucket
    What we're looking for: Successful connection to your djangoblogplatform bucket
    """
    print_header("Testing S3 Bucket Access")

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # Try to list objects in the bucket (this tests bucket access)
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            MaxKeys=5  # Just get a few objects to test access
        )

        print_success(f"Successfully connected to bucket: {settings.AWS_STORAGE_BUCKET_NAME}")

        # Show some info about the bucket contents
        if 'Contents' in response:
            print_info(f"Bucket contains {len(response['Contents'])} objects (showing up to 5)")
            for obj in response['Contents'][:5]:
                print_info(f"  - {obj['Key']} (size: {obj['Size']} bytes)")
        else:
            print_info("Bucket is empty or no objects found")

        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print_error(f"Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' does not exist")
        elif error_code == 'AccessDenied':
            print_error(f"Access denied to bucket '{settings.AWS_STORAGE_BUCKET_NAME}'")
            print_info("Check that your AWS user has S3 permissions")
        else:
            print_error(f"S3 bucket access error: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error accessing S3 bucket: {e}")
        return False


def test_django_file_upload():
    """
    Test 5: Test if Django can upload files through the storage backend
    What we're looking for: Successful file upload using Django's storage system
    """
    print_header("Testing Django File Upload")

    try:
        # Create a test file
        test_content = ContentFile(b'This is a test file to verify S3 upload functionality')
        test_filename = 'diagnostic_test_file.txt'

        print_info(f"Attempting to upload test file: {test_filename}")

        # Try to save the file using Django's default storage
        saved_path = default_storage.save(test_filename, test_content)

        print_success(f"File uploaded successfully to: {saved_path}")

        # Try to get the URL for the uploaded file
        file_url = default_storage.url(saved_path)
        print_info(f"File URL: {file_url}")

        # Try to check if the file exists
        if default_storage.exists(saved_path):
            print_success("File exists in storage")
        else:
            print_warning("File upload reported success but file not found")

        # Clean up - delete the test file
        default_storage.delete(saved_path)
        print_info("Test file deleted successfully")

        return True, saved_path

    except Exception as e:
        print_error(f"Django file upload failed: {e}")
        print_info("Full error details:")
        traceback.print_exc()
        return False, None


def test_acl_permissions():
    """
    Test 6: Test if we can set ACL permissions on uploaded files
    What we're looking for: Ability to set public-read permissions
    """
    print_header("Testing ACL Permission Setting")

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        # Upload a test file directly via boto3 to test ACL setting
        test_key = 'diagnostic_acl_test.txt'
        test_content = b'Test file for ACL permission testing'

        print_info(f"Uploading test file with public-read ACL: {test_key}")

        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=test_key,
            Body=test_content,
            ACL='public-read'
        )

        print_success("Successfully uploaded file with public-read ACL")

        # Check the ACL to verify it was set correctly
        acl_response = s3_client.get_object_acl(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=test_key
        )

        # Look for public read access in the ACL
        public_read_found = False
        for grant in acl_response['Grants']:
            grantee = grant['Grantee']
            if grantee.get('Type') == 'Group' and 'AllUsers' in grantee.get('URI', ''):
                if grant['Permission'] == 'READ':
                    public_read_found = True
                    break

        if public_read_found:
            print_success("Public read access confirmed in ACL")
        else:
            print_warning("Public read access not found in ACL")

        # Clean up
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=test_key
        )
        print_info("Test file deleted successfully")

        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print_error("Access denied when trying to set ACL permissions")
            print_info("Your AWS user may not have s3:PutObjectAcl permission")
        else:
            print_error(f"ACL permission test failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error testing ACL permissions: {e}")
        return False


def main():
    """
    Main diagnostic function that runs all tests
    """
    print(f"{Colors.BOLD}S3 Integration Diagnostic Test{Colors.END}")
    print("This test will systematically check your Django S3 integration")
    print("=" * 60)

    # Run all tests in order
    tests_passed = 0
    total_tests = 6

    if test_environment_variables():
        tests_passed += 1

    if test_django_settings():
        tests_passed += 1

    if test_aws_credentials():
        tests_passed += 1

    if test_s3_bucket_access():
        tests_passed += 1

    upload_success, upload_path = test_django_file_upload()
    if upload_success:
        tests_passed += 1

    if test_acl_permissions():
        tests_passed += 1

    # Summary
    print_header("Diagnostic Summary")

    if tests_passed == total_tests:
        print_success(f"All {total_tests} tests passed! Your S3 integration should be working.")
        print_info("If you're still experiencing issues, they may be specific to your Django views or forms.")
    else:
        print_error(f"Only {tests_passed} out of {total_tests} tests passed.")
        print_info("Focus on fixing the failed tests above to resolve your S3 integration issues.")

    print("\n" + "=" * 60)
    print("Test completed. Check the results above to identify any issues.")


if __name__ == "__main__":
    main()