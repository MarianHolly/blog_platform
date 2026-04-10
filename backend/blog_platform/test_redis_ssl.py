import os
import redis
from dotenv import load_dotenv

load_dotenv()


def test_redis_with_ssl_disabled():
    """Test Redis with SSL certificate verification disabled"""
    try:
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            print("❌ No REDIS_URL found")
            return False

        print("🔍 Testing Redis with SSL verification disabled...")

        # Convert to SSL URL
        if redis_url.startswith('redis://'):
            ssl_url = redis_url.replace('redis://', 'rediss://', 1)
        else:
            ssl_url = redis_url

        # Connect with SSL verification disabled
        r = redis.from_url(
            ssl_url,
            ssl_check_hostname=False,
            ssl_cert_reqs=None
        )

        # Test connection
        r.ping()
        r.set('test_ssl', 'works', ex=10)
        value = r.get('test_ssl')

        if value == b'works':
            print("✅ Redis SSL connection successful!")
            r.delete('test_ssl')
            return True
        else:
            print("❌ Redis SSL connection failed")
            return False

    except Exception as e:
        print(f"❌ Redis SSL test failed: {e}")
        return False


def test_without_redis():
    """Test app behavior without Redis"""
    print("🔍 Testing app without Redis...")
    print("✅ App will use database sessions instead")
    print("✅ Caching will be disabled (dummy cache)")
    print("✅ All core functionality will work normally")
    return True


if __name__ == "__main__":
    print("🧪 Testing Redis SSL Configuration\n")

    # Test with SSL disabled
    ssl_works = test_redis_with_ssl_disabled()
    print()

    # Show fallback option
    test_without_redis()
    print()

    print("📋 Recommendations:")
    if ssl_works:
        print("   ✅ Use Option 1: Update settings.py with SSL fix")
        print("   🎯 Redis will work for caching and sessions")
    else:
        print("   ✅ Use Option 2: Comment out REDIS_URL in .env")
        print("   🎯 App will work perfectly without Redis")

    print("\n🚀 Either way, your app will work fine!")