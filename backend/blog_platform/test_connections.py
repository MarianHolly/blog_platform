# test_connections.py (UPDATED VERSION)
import os
from dotenv import load_dotenv

load_dotenv()


def test_redis_connection():
    """Test Redis connection with proper Upstash handling"""
    try:
        import redis

        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            print("❌ REDIS_URL not found in environment variables")
            return False

        print(f"🔍 Testing Redis connection...")
        print(f"🔗 Redis URL: {redis_url[:50]}...")

        # Handle Upstash Redis (requires SSL)
        if 'upstash.io' in redis_url:
            print("🔒 Detected Upstash Redis - using SSL connection")

            # Convert to SSL URL if needed
            if redis_url.startswith('redis://'):
                ssl_url = redis_url.replace('redis://', 'rediss://', 1)
            else:
                ssl_url = redis_url

            # Connect with SSL settings
            r = redis.from_url(
                ssl_url,
                ssl_check_hostname=False,
                ssl_cert_reqs=None
            )
        else:
            # Regular Redis connection
            print("🔓 Using regular Redis connection")
            r = redis.from_url(redis_url)

        # Test connection
        print("🏓 Testing ping...")
        r.ping()

        print("📝 Testing read/write...")
        r.set('test_key', 'test_value', ex=10)  # Set with 10 second expiry
        value = r.get('test_key')

        if value == b'test_value':
            print("✅ Redis connection successful!")
            print("🎯 Redis read/write test passed")

            # Clean up
            r.delete('test_key')
            return True
        else:
            print("❌ Redis read/write test failed")
            return False

    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False


def test_database_connection():
    """Test PostgreSQL connection"""
    try:
        import psycopg2

        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False

        print(f"🔍 Testing database connection...")
        print(f"🔗 Database URL: {database_url[:50]}...")

        # Parse the URL and connect
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        print(f"✅ Database connection successful!")
        print(f"📊 PostgreSQL version: {version[0][:50]}...")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_cloudinary_connection():
    """Test Cloudinary connection"""
    try:
        import cloudinary
        import cloudinary.api

        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')

        if not all([cloud_name, api_key, api_secret]):
            print("❌ Cloudinary credentials not found")
            return False

        print(f"🔍 Testing Cloudinary connection...")

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )

        # Test API connection
        result = cloudinary.api.ping()

        if result.get('status') == 'ok':
            print("✅ Cloudinary connection successful!")
            return True
        else:
            print(f"❌ Cloudinary connection failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Cloudinary connection failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing external service connections...\n")

    # Test Redis first (the problematic one)
    redis_ok = test_redis_connection()
    print()

    db_ok = test_database_connection()
    print()

    cloudinary_ok = test_cloudinary_connection()
    print()

    print("📋 Summary:")
    print(f"   Redis: {'✅' if redis_ok else '❌'}")
    print(f"   Database: {'✅' if db_ok else '❌'}")
    print(f"   Cloudinary: {'✅' if cloudinary_ok else '❌'}")

    if all([redis_ok, db_ok, cloudinary_ok]):
        print("\n🎉 All connections successful! Your app should work.")
    else:
        print("\n⚠️  Some connections failed. Check the errors above.")

        if not redis_ok:
            print("\n💡 Redis troubleshooting:")
            print("   1. Check if REDIS_URL is correct in .env")
            print("   2. Try updating redis library: pip install redis --upgrade")
            print("   3. Consider skipping Redis for now (app will use database sessions)")