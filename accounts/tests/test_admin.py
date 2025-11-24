"""
Tests for ProfileAdmin and BulletinAdmin interfaces.

Tests cover:
- List display configuration and field display methods
- Filtering by role (reader, writer, admin) and activity status (active, inactive)
- Search functionality by username and email
- Engagement metrics calculation and display
- Bulletin information display for writers
- Permission checks (admin-only access)
- Readonly fields configuration
- Detail view display methods
"""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from accounts.models import Profile
from accounts.admin import ProfileAdmin, BulletinAdmin
from content.models import Article, Bulletin, Subscription
from engagement.models import Like, Comment


class ProfileAdminTestCase(TestCase):
    """Base test case for ProfileAdmin tests with helper methods."""

    @classmethod
    def setUpTestData(cls):
        """Create test data for ProfileAdmin tests."""
        # Create admin user
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        cls.admin_profile = Profile.objects.create(user=cls.admin_user, role='admin')

        # Create reader user
        cls.reader_user = User.objects.create_user(
            username='reader1',
            email='reader1@test.com',
            password='pass123',
            first_name='Alice',
            last_name='Reader'
        )
        cls.reader_profile = Profile.objects.create(user=cls.reader_user, role='reader')

        # Create writer user
        cls.writer_user = User.objects.create_user(
            username='writer1',
            email='writer1@test.com',
            password='pass123',
            first_name='Bob',
            last_name='Writer'
        )
        cls.writer_profile = Profile.objects.create(user=cls.writer_user, role='writer')
        cls.writer_bulletin = Bulletin.objects.create(
            owner=cls.writer_profile,
            title='Bob\'s Blog',
            slug='bobs-blog',
            description='Articles by Bob'
        )

        # Create articles for writer
        for i in range(3):
            Article.objects.create(
                title=f'Article {i+1}',
                content='<p>Test content</p>',
                bulletin=cls.writer_bulletin,
                status='published'
            )

        # Create likes on writer's articles
        articles = cls.writer_bulletin.articles.all()[:2]
        for article in articles:
            Like.objects.create(user=cls.reader_user, article=article)

        # Create comments on writer's articles
        for article in articles:
            Comment.objects.create(
                author=cls.reader_user,
                article=article,
                content='Great article!'
            )

        # Create reader engagement
        Subscription.objects.create(subscriber=cls.reader_profile, bulletin=cls.writer_bulletin)

        # Create another subscription
        writer2_user = User.objects.create_user(
            username='writer2',
            email='writer2@test.com',
            password='pass123'
        )
        writer2_profile = Profile.objects.create(user=writer2_user, role='writer')
        writer2_bulletin = Bulletin.objects.create(
            owner=writer2_profile,
            title='Writer 2 Blog',
            slug='writer-2-blog'
        )
        Subscription.objects.create(subscriber=cls.reader_profile, bulletin=writer2_bulletin)

    def setUp(self):
        """Set up for each test."""
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = ProfileAdmin(Profile, self.site)


class ProfileAdminListDisplayTest(ProfileAdminTestCase):
    """Tests for ProfileAdmin list display configuration."""

    def test_list_display_configured(self):
        """list_display should be configured with required fields."""
        expected_fields = [
            'username_display',
            'email_display',
            'role',
            'is_active_display',
            'articles_count',
            'engagement_summary',
            'last_login_display',
            'created_display'
        ]
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_username_display_method_exists(self):
        """username_display method should exist and work."""
        self.assertTrue(hasattr(self.admin, 'username_display'))
        result = self.admin.username_display(self.reader_profile)
        self.assertEqual(result, 'reader1')

    def test_email_display_method_exists(self):
        """email_display method should exist and work."""
        self.assertTrue(hasattr(self.admin, 'email_display'))
        result = self.admin.email_display(self.reader_profile)
        self.assertEqual(result, 'reader1@test.com')

    def test_is_active_display_shows_status(self):
        """is_active_display should show active/inactive status."""
        result = self.admin.is_active_display(self.reader_profile)
        self.assertIn('Active', result)
        self.assertIn('✓', result)

    def test_is_active_display_shows_inactive(self):
        """is_active_display should show inactive status correctly."""
        self.reader_user.is_active = False
        self.reader_user.save()
        result = self.admin.is_active_display(self.reader_profile)
        self.assertIn('Inactive', result)
        self.assertIn('✗', result)

    def test_articles_count_for_writer(self):
        """articles_count should show count for writers."""
        result = self.admin.articles_count(self.writer_profile)
        self.assertEqual(result, 3)

    def test_articles_count_for_reader(self):
        """articles_count should show '—' for readers."""
        result = self.admin.articles_count(self.reader_profile)
        self.assertEqual(result, '—')

    def test_engagement_summary_for_writer(self):
        """engagement_summary should show likes and comments for writers."""
        result = self.admin.engagement_summary(self.writer_profile)
        self.assertIn('L:', result)
        self.assertIn('C:', result)
        self.assertEqual(result, 'L:2 C:2')

    def test_engagement_summary_for_reader(self):
        """engagement_summary should show likes and comments for readers."""
        result = self.admin.engagement_summary(self.reader_profile)
        self.assertEqual(result, 'L:2 C:2')

    def test_last_login_display(self):
        """last_login_display should show last login date or 'Never'."""
        result = self.admin.last_login_display(self.reader_profile)
        self.assertIn('Never', result)

    def test_created_display_shows_date(self):
        """created_display should show creation date in YYYY-MM-DD format."""
        result = self.admin.created_display(self.reader_profile)
        self.assertRegex(result, r'\d{4}-\d{2}-\d{2}')


class ProfileAdminFilterTest(ProfileAdminTestCase):
    """Tests for ProfileAdmin filtering."""

    def test_list_filter_configured(self):
        """list_filter should include role and is_active."""
        self.assertIn('role', self.admin.list_filter)
        self.assertIn('user__is_active', self.admin.list_filter)

    def test_can_filter_by_role_reader(self):
        """Admin should be able to filter by reader role."""
        readers = Profile.objects.filter(role='reader')
        self.assertTrue(readers.exists())
        self.assertEqual(readers.count(), 1)
        self.assertEqual(readers.first(), self.reader_profile)

    def test_can_filter_by_role_writer(self):
        """Admin should be able to filter by writer role."""
        writers = Profile.objects.filter(role='writer')
        self.assertTrue(writers.exists())
        self.assertIn(self.writer_profile, writers)

    def test_can_filter_by_role_admin(self):
        """Admin should be able to filter by admin role."""
        admins = Profile.objects.filter(role='admin')
        self.assertTrue(admins.exists())
        self.assertEqual(admins.count(), 1)

    def test_can_filter_by_active_status(self):
        """Admin should be able to filter by active status."""
        active_users = Profile.objects.filter(user__is_active=True)
        self.assertTrue(active_users.count() > 0)

    def test_can_filter_by_inactive_status(self):
        """Admin should be able to filter by inactive status."""
        self.reader_user.is_active = False
        self.reader_user.save()
        inactive_users = Profile.objects.filter(user__is_active=False)
        self.assertTrue(inactive_users.exists())
        self.assertIn(self.reader_profile, inactive_users)


class ProfileAdminSearchTest(ProfileAdminTestCase):
    """Tests for ProfileAdmin search functionality."""

    def test_search_fields_configured(self):
        """search_fields should include username, email, first_name, last_name."""
        expected_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
        self.assertEqual(self.admin.search_fields, expected_fields)

    def test_can_search_by_username(self):
        """Admin should be able to search by username."""
        users = Profile.objects.filter(user__username__icontains='reader')
        self.assertTrue(users.exists())
        self.assertIn(self.reader_profile, users)

    def test_can_search_by_email(self):
        """Admin should be able to search by email."""
        users = Profile.objects.filter(user__email__icontains='writer1')
        self.assertTrue(users.exists())
        self.assertIn(self.writer_profile, users)

    def test_can_search_by_first_name(self):
        """Admin should be able to search by first name."""
        users = Profile.objects.filter(user__first_name__icontains='Bob')
        self.assertTrue(users.exists())
        self.assertIn(self.writer_profile, users)

    def test_can_search_by_last_name(self):
        """Admin should be able to search by last name."""
        users = Profile.objects.filter(user__last_name__icontains='Reader')
        self.assertTrue(users.exists())
        self.assertIn(self.reader_profile, users)


class ProfileAdminEngagementMetricsTest(ProfileAdminTestCase):
    """Tests for engagement metrics display."""

    def test_articles_count_calculation(self):
        """get_articles_count should return correct count for writers."""
        count = self.writer_profile.get_articles_count()
        self.assertEqual(count, 3)

    def test_likes_received_calculation(self):
        """get_likes_received_count should return likes on writer's articles."""
        count = self.writer_profile.get_likes_received_count()
        self.assertEqual(count, 2)

    def test_comments_received_calculation(self):
        """get_comments_received_count should return comments on writer's articles."""
        count = self.writer_profile.get_comments_received_count()
        self.assertEqual(count, 2)

    def test_articles_liked_calculation(self):
        """get_articles_liked_count should return articles liked by reader."""
        count = self.reader_profile.get_articles_liked_count()
        self.assertEqual(count, 2)

    def test_comments_posted_calculation(self):
        """get_comments_posted_count should return comments posted by reader."""
        count = self.reader_profile.get_comments_posted_count()
        self.assertEqual(count, 2)

    def test_subscriptions_count_calculation(self):
        """get_subscriptions_count should return bulletin subscriptions."""
        count = self.reader_profile.get_subscriptions_count()
        self.assertEqual(count, 2)

    def test_bulletin_info_for_writer(self):
        """get_bulletin_info should return bulletin details for writers."""
        info = self.writer_profile.get_bulletin_info()
        self.assertIsNotNone(info)
        self.assertEqual(info['title'], 'Bob\'s Blog')
        self.assertEqual(info['articles'], 3)
        self.assertEqual(info['subscribers'], 1)

    def test_bulletin_info_for_reader(self):
        """get_bulletin_info should return None for readers."""
        info = self.reader_profile.get_bulletin_info()
        self.assertIsNone(info)

    def test_articles_count_readonly_display(self):
        """articles_count_readonly should display article count for writers."""
        result = self.admin.articles_count_readonly(self.writer_profile)
        self.assertEqual(result, 3)

    def test_articles_count_readonly_for_reader(self):
        """articles_count_readonly should show '—' for readers."""
        result = self.admin.articles_count_readonly(self.reader_profile)
        self.assertEqual(result, '—')

    def test_likes_received_readonly_display(self):
        """likes_received_readonly should display likes count for writers."""
        result = self.admin.likes_received_readonly(self.writer_profile)
        self.assertEqual(result, 2)

    def test_comments_received_readonly_display(self):
        """comments_received_readonly should display comments count for writers."""
        result = self.admin.comments_received_readonly(self.writer_profile)
        self.assertEqual(result, 2)

    def test_articles_liked_readonly_display(self):
        """articles_liked_readonly should display articles liked by reader."""
        result = self.admin.articles_liked_readonly(self.reader_profile)
        self.assertEqual(result, 2)

    def test_comments_posted_readonly_display(self):
        """comments_posted_readonly should display comments posted by reader."""
        result = self.admin.comments_posted_readonly(self.reader_profile)
        self.assertEqual(result, 2)

    def test_subscriptions_readonly_display(self):
        """subscriptions_readonly should display bulletin subscriptions."""
        result = self.admin.subscriptions_readonly(self.reader_profile)
        self.assertEqual(result, 2)

    def test_bulletin_info_readonly_display(self):
        """bulletin_info_readonly should display bulletin info for writers."""
        result = self.admin.bulletin_info_readonly(self.writer_profile)
        self.assertIn('Bob\'s Blog', result)
        self.assertIn('3 articles', result)
        self.assertIn('1 subscriber', result)


class ProfileAdminPermissionTest(ProfileAdminTestCase):
    """Tests for permission checks."""

    def setUp(self):
        """Set up for each test."""
        super().setUp()
        self.factory = RequestFactory()

    def test_admin_access_for_superuser(self):
        """Admin should be accessible to superusers."""
        request = self.factory.get('/admin/accounts/profile/')
        request.user = self.admin_user
        has_access = self.admin.has_permission(request, 'change')
        self.assertTrue(has_access)

    def test_admin_access_denied_for_non_admin(self):
        """Admin should be inaccessible to non-admin users."""
        request = self.factory.get('/admin/accounts/profile/')
        request.user = self.reader_user
        has_access = self.admin.has_permission(request, 'change')
        self.assertFalse(has_access)


class BulletinAdminTestCase(TestCase):
    """Base test case for BulletinAdmin tests."""

    @classmethod
    def setUpTestData(cls):
        """Create test data for BulletinAdmin tests."""
        # Create writer and bulletin
        cls.writer_user = User.objects.create_user(
            username='writer1',
            email='writer1@test.com',
            password='pass123',
            first_name='Bob',
            last_name='Writer'
        )
        cls.writer_profile = Profile.objects.create(user=cls.writer_user, role='writer')
        cls.bulletin = Bulletin.objects.create(
            owner=cls.writer_profile,
            title='Bob\'s Blog',
            slug='bobs-blog',
            description='Articles by Bob'
        )

        # Create articles
        for i in range(5):
            Article.objects.create(
                title=f'Article {i+1}',
                content='<p>Test content</p>',
                bulletin=cls.bulletin,
                status='published'
            )

        # Create reader and subscription
        cls.reader_user = User.objects.create_user(
            username='reader1',
            email='reader1@test.com',
            password='pass123'
        )
        cls.reader_profile = Profile.objects.create(user=cls.reader_user, role='reader')
        Subscription.objects.create(subscriber=cls.reader_profile, bulletin=cls.bulletin)

        # Create another subscription
        reader2_user = User.objects.create_user(username='reader2', password='pass123')
        reader2_profile = Profile.objects.create(user=reader2_user, role='reader')
        Subscription.objects.create(subscriber=reader2_profile, bulletin=cls.bulletin)

    def setUp(self):
        """Set up for each test."""
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = BulletinAdmin(Bulletin, self.site)


class BulletinAdminListDisplayTest(BulletinAdminTestCase):
    """Tests for BulletinAdmin list display."""

    def test_list_display_configured(self):
        """list_display should include title, writer, articles, subscribers, created."""
        expected_fields = ['title', 'writer_display', 'articles_count', 'subscribers_count', 'created_display']
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_writer_display_shows_name_and_username(self):
        """writer_display should show writer's name and username."""
        result = self.admin.writer_display(self.bulletin)
        self.assertIn('Bob Writer', result)
        self.assertIn('writer1', result)

    def test_articles_count_shows_correct_number(self):
        """articles_count should show correct number of articles."""
        result = self.admin.articles_count(self.bulletin)
        self.assertEqual(result, 5)

    def test_subscribers_count_shows_correct_number(self):
        """subscribers_count should show correct number of subscribers."""
        result = self.admin.subscribers_count(self.bulletin)
        self.assertEqual(result, 2)

    def test_created_display_shows_date(self):
        """created_display should show creation date in YYYY-MM-DD format."""
        result = self.admin.created_display(self.bulletin)
        self.assertRegex(result, r'\d{4}-\d{2}-\d{2}')


class BulletinAdminSearchTest(BulletinAdminTestCase):
    """Tests for BulletinAdmin search functionality."""

    def test_search_fields_configured(self):
        """search_fields should include title, username, name fields."""
        self.assertIn('title', self.admin.search_fields)
        self.assertIn('owner__user__username', self.admin.search_fields)

    def test_can_search_by_title(self):
        """Admin should be able to search by bulletin title."""
        bulletins = Bulletin.objects.filter(title__icontains='Blog')
        self.assertTrue(bulletins.exists())
        self.assertIn(self.bulletin, bulletins)

    def test_can_search_by_writer_username(self):
        """Admin should be able to search by writer username."""
        bulletins = Bulletin.objects.filter(owner__user__username__icontains='writer')
        self.assertTrue(bulletins.exists())
        self.assertIn(self.bulletin, bulletins)


class BulletinAdminFilterTest(BulletinAdminTestCase):
    """Tests for BulletinAdmin filtering."""

    def test_list_filter_configured(self):
        """list_filter should include created and updated."""
        self.assertIn('created', self.admin.list_filter)
        self.assertIn('updated', self.admin.list_filter)


class BulletinAdminPermissionTest(BulletinAdminTestCase):
    """Tests for BulletinAdmin permission checks."""

    def setUp(self):
        """Set up for each test."""
        super().setUp()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        Profile.objects.create(user=self.admin_user, role='admin')
        self.factory = RequestFactory()

    def test_admin_access_for_superuser(self):
        """Admin should be accessible to superusers."""
        request = self.factory.get('/admin/content/bulletin/')
        request.user = self.admin_user
        has_access = self.admin.has_permission(request, 'change')
        self.assertTrue(has_access)

    def test_admin_access_denied_for_non_admin(self):
        """Admin should be inaccessible to non-admin users."""
        request = self.factory.get('/admin/content/bulletin/')
        request.user = self.writer_user
        has_access = self.admin.has_permission(request, 'change')
        self.assertFalse(has_access)
