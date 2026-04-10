"""
Tests for ProfileAdmin interface.

Tests cover:
- List display configuration
- Filtering by role and activity status
- Search functionality
- Engagement metrics calculation
- Bulletin information display
- Permission checks
"""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from accounts.models import Profile
from accounts.admin import ProfileAdmin
from content.models import Article, Bulletin, Subscription
from engagement.models import Like, Comment


class ProfileAdminListDisplayTest(TestCase):
    """Tests for ProfileAdmin list display configuration."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        cls.writer_user = User.objects.create_user(
            username='writer1', email='writer1@test.com', password='pass123',
            first_name='Bob', last_name='Writer'
        )
        cls.writer_profile = cls.writer_user.profile  # Use auto-created profile

        cls.writer_profile.role = 'writer'

        cls.writer_profile.save()
        cls.writer_bulletin = Bulletin.objects.create(
            owner=cls.writer_profile, title='Bob\'s Blog', slug='bobs-blog'
        )
        for i in range(3):
            Article.objects.create(
                title=f'Article {i+1}', content='<p>Test</p>',
                bulletin=cls.writer_bulletin, status='published'
            )

        cls.reader_user = User.objects.create_user(
            username='reader1', email='reader1@test.com', password='pass123'
        )
        cls.reader_profile = cls.reader_user.profile  # Use auto-created profile

        cls.reader_profile.role = 'reader'

        cls.reader_profile.save()

    def setUp(self):
        """Set up for each test."""
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = ProfileAdmin(Profile, self.site)

    def test_list_display_configured(self):
        """list_display should have required fields."""
        expected = [
            'username_display', 'email_display', 'role', 'is_active_display',
            'articles_count', 'engagement_summary', 'last_login_display', 'created_display'
        ]
        self.assertEqual(self.admin.list_display, expected)

    def test_list_filter_configured(self):
        """list_filter should include role and is_active."""
        self.assertIn('role', self.admin.list_filter)
        self.assertIn('user__is_active', self.admin.list_filter)

    def test_search_fields_configured(self):
        """search_fields should be configured."""
        self.assertIn('user__username', self.admin.search_fields)
        self.assertIn('user__email', self.admin.search_fields)

    def test_username_display(self):
        """username_display should return username."""
        result = self.admin.username_display(self.reader_profile)
        self.assertEqual(result, 'reader1')

    def test_email_display(self):
        """email_display should return email."""
        result = self.admin.email_display(self.reader_profile)
        self.assertEqual(result, 'reader1@test.com')

    def test_is_active_display_active(self):
        """is_active_display should show active status."""
        result = self.admin.is_active_display(self.reader_profile)
        self.assertIn('Active', result)
        self.assertIn('✓', result)

    def test_is_active_display_inactive(self):
        """is_active_display should show inactive status."""
        self.reader_user.is_active = False
        self.reader_user.save()
        result = self.admin.is_active_display(self.reader_profile)
        self.assertIn('Inactive', result)
        self.assertIn('✗', result)

    def test_articles_count_for_writer(self):
        """articles_count should show article count for writers."""
        result = self.admin.articles_count(self.writer_profile)
        self.assertEqual(result, 3)

    def test_articles_count_for_reader(self):
        """articles_count should show '—' for readers."""
        result = self.admin.articles_count(self.reader_profile)
        self.assertEqual(result, '—')

    def test_created_display_format(self):
        """created_display should show date in YYYY-MM-DD format."""
        result = self.admin.created_display(self.reader_profile)
        self.assertRegex(result, r'\d{4}-\d{2}-\d{2}')

    def test_last_login_display(self):
        """last_login_display should show 'Never' for new users."""
        result = self.admin.last_login_display(self.reader_profile)
        self.assertIn('Never', result)


class ProfileAdminFilterTest(TestCase):
    """Tests for ProfileAdmin filtering."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        cls.reader_user = User.objects.create_user(username='reader1', password='pass123')
        cls.reader_profile = cls.reader_user.profile  # Use auto-created profile

        cls.reader_profile.role = 'reader'

        cls.reader_profile.save()

        cls.writer_user = User.objects.create_user(username='writer1', password='pass123')
        cls.writer_profile = cls.writer_user.profile  # Use auto-created profile

        cls.writer_profile.role = 'writer'

        cls.writer_profile.save()

    def test_filter_by_reader_role(self):
        """Can filter by reader role."""
        readers = Profile.objects.filter(role='reader')
        self.assertIn(self.reader_profile, readers)

    def test_filter_by_writer_role(self):
        """Can filter by writer role."""
        writers = Profile.objects.filter(role='writer')
        self.assertIn(self.writer_profile, writers)

    def test_filter_by_active_status(self):
        """Can filter by active status."""
        active = Profile.objects.filter(user__is_active=True)
        self.assertTrue(active.exists())

    def test_filter_by_inactive_status(self):
        """Can filter by inactive status."""
        self.reader_user.is_active = False
        self.reader_user.save()
        inactive = Profile.objects.filter(user__is_active=False)
        self.assertIn(self.reader_profile, inactive)


class ProfileAdminSearchTest(TestCase):
    """Tests for ProfileAdmin search."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        cls.user = User.objects.create_user(
            username='testuser', email='test@example.com',
            first_name='John', last_name='Doe', password='pass123'
        )
        cls.profile = cls.user.profile  # Use auto-created profile

        cls.profile.role = 'reader'

        cls.profile.save()

    def test_search_by_username(self):
        """Can search by username."""
        users = Profile.objects.filter(user__username__icontains='testuser')
        self.assertIn(self.profile, users)

    def test_search_by_email(self):
        """Can search by email."""
        users = Profile.objects.filter(user__email__icontains='test@example')
        self.assertIn(self.profile, users)

    def test_search_by_first_name(self):
        """Can search by first name."""
        users = Profile.objects.filter(user__first_name__icontains='John')
        self.assertIn(self.profile, users)

    def test_search_by_last_name(self):
        """Can search by last name."""
        users = Profile.objects.filter(user__last_name__icontains='Doe')
        self.assertIn(self.profile, users)


class ProfileAdminEngagementMetricsTest(TestCase):
    """Tests for engagement metrics methods."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        cls.writer_user = User.objects.create_user(username='writer1', password='pass123')
        cls.writer_profile = cls.writer_user.profile  # Use auto-created profile

        cls.writer_profile.role = 'writer'

        cls.writer_profile.save()
        cls.writer_bulletin = Bulletin.objects.create(
            owner=cls.writer_profile, title='Blog', slug='blog'
        )
        Article.objects.create(
            title='Art1', content='<p>Test</p>',
            bulletin=cls.writer_bulletin, status='published'
        )

        cls.reader_user = User.objects.create_user(username='reader1', password='pass123')
        cls.reader_profile = cls.reader_user.profile  # Use auto-created profile

        cls.reader_profile.role = 'reader'

        cls.reader_profile.save()

    def test_get_articles_count_for_writer(self):
        """get_articles_count should return article count for writers."""
        count = self.writer_profile.get_articles_count()
        self.assertEqual(count, 1)

    def test_get_articles_count_for_reader(self):
        """get_articles_count should return 0 for readers."""
        count = self.reader_profile.get_articles_count()
        self.assertEqual(count, 0)

    def test_get_subscriptions_count(self):
        """get_subscriptions_count should return subscription count."""
        Subscription.objects.create(
            subscriber=self.reader_profile, bulletin=self.writer_bulletin
        )
        count = self.reader_profile.get_subscriptions_count()
        self.assertEqual(count, 1)

    def test_get_bulletin_info_for_writer(self):
        """get_bulletin_info should return bulletin info for writers."""
        info = self.writer_profile.get_bulletin_info()
        self.assertIsNotNone(info)
        self.assertEqual(info['title'], 'Blog')
        self.assertEqual(info['articles'], 1)

    def test_get_bulletin_info_for_reader(self):
        """get_bulletin_info should return None for readers."""
        info = self.reader_profile.get_bulletin_info()
        self.assertIsNone(info)

    def test_articles_count_readonly_display(self):
        """articles_count_readonly should display count for writers."""
        site = AdminSite()
        admin = ProfileAdmin(Profile, site)
        result = admin.articles_count_readonly(self.writer_profile)
        self.assertEqual(result, 1)

    def test_subscriptions_readonly_display(self):
        """subscriptions_readonly should display subscription count."""
        site = AdminSite()
        admin = ProfileAdmin(Profile, site)
        result = admin.subscriptions_readonly(self.reader_profile)
        self.assertEqual(result, 0)


class ProfileAdminPermissionTest(TestCase):
    """Tests for ProfileAdmin permission checks."""

    def setUp(self):
        """Set up for each test."""
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = ProfileAdmin(Profile, self.site)

        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='admin123'
        )
        self.admin_user.profile.role = 'admin'  # Use auto-created profile

        self.admin_user.profile.save()

        self.reader_user = User.objects.create_user(
            username='reader', email='reader@test.com', password='pass123'
        )
        self.reader_user.profile.role = 'reader'  # Use auto-created profile

        self.reader_user.profile.save()

    def test_admin_access_for_superuser(self):
        """Admin should be accessible to superusers."""
        request = self.factory.get('/admin/accounts/profile/')
        request.user = self.admin_user
        has_access = self.admin.has_permission(request)
        self.assertTrue(has_access)

    def test_admin_access_denied_for_non_admin(self):
        """Admin should be inaccessible to non-admin users."""
        request = self.factory.get('/admin/accounts/profile/')
        request.user = self.reader_user
        has_access = self.admin.has_permission(request)
        self.assertFalse(has_access)
