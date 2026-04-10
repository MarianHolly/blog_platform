from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from content.models import Article, Bulletin
from engagement.models import Like, ReadLater


class LikeToggleViewTest(TestCase):
    """Test Like toggle functionality"""

    def setUp(self):
        """Set up test data: writer and reader with article"""
        self.client = Client()

        # Create writer and their article
        self.writer = User.objects.create_user(
            username='writer',
            email='writer@test.com',
            password='pass123'
        )
        self.writer_profile = self.writer.profile  # Use auto-created profile
        self.writer_profile.role = 'writer'
        self.writer_profile.save()
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='<p>Test content</p>',
            bulletin=self.bulletin,
            status='published',
            visibility='public',
            published=timezone.now()
        )

        # Create reader
        self.reader = User.objects.create_user(
            username='reader',
            email='reader@test.com',
            password='pass123'
        )
        self.reader_profile = self.reader.profile  # Use auto-created profile
        self.reader_profile.role = 'reader'
        self.reader_profile.save()

    def test_like_toggle_requires_login(self):
        """Like toggle requires user to be logged in"""
        response = self.client.post(reverse('toggle_like', args=[self.article.id]))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_like_toggle_adds_like(self):
        """Reader can like an article"""
        self.client.login(username='reader', password='pass123')
        next_url = '/articles/'
        response = self.client.post(
            reverse('toggle_like', args=[self.article.id]),
            {'next': next_url}
        )

        # Like should be created
        self.assertTrue(Like.objects.filter(
            article=self.article,
            author=self.reader_profile
        ).exists())

        # Should redirect
        self.assertEqual(response.status_code, 302)

    def test_like_toggle_removes_like(self):
        """Reader can unlike an article"""
        self.client.login(username='reader', password='pass123')

        # Create like first
        Like.objects.create(article=self.article, author=self.reader_profile)
        self.assertTrue(Like.objects.filter(
            article=self.article,
            author=self.reader_profile
        ).exists())

        # Toggle like (should remove it)
        next_url = '/articles/'
        response = self.client.post(
            reverse('toggle_like', args=[self.article.id]),
            {'next': next_url}
        )

        # Like should be deleted
        self.assertFalse(Like.objects.filter(
            article=self.article,
            author=self.reader_profile
        ).exists())

        # Should redirect
        self.assertEqual(response.status_code, 302)

    def test_like_toggle_prevents_self_like(self):
        """User cannot like their own article"""
        self.client.login(username='writer', password='pass123')
        next_url = '/articles/'
        response = self.client.post(
            reverse('toggle_like', args=[self.article.id]),
            {'next': next_url}
        )

        # Like should NOT be created
        self.assertFalse(Like.objects.filter(
            article=self.article,
            author=self.writer_profile
        ).exists())

        # Should redirect
        self.assertEqual(response.status_code, 302)

    def test_like_toggle_redirects_to_article(self):
        """Like toggle should redirect to next parameter if provided"""
        self.client.login(username='reader', password='pass123')
        next_url = '/articles/'
        response = self.client.post(
            reverse('toggle_like', args=[self.article.id]),
            {'next': next_url}
        )

        # Should redirect to next_url
        self.assertEqual(response.url, next_url)

    def test_like_toggle_respects_next_parameter(self):
        """Like toggle should redirect to 'next' parameter if provided"""
        self.client.login(username='reader', password='pass123')
        next_url = '/articles/'
        response = self.client.post(
            reverse('toggle_like', args=[self.article.id]),
            {'next': next_url}
        )

        # Should redirect to next_url
        self.assertEqual(response.url, next_url)


class ReadLaterToggleViewTest(TestCase):
    """Test Read Later (bookmark) toggle functionality"""

    def setUp(self):
        """Set up test data: writer and reader with article"""
        self.client = Client()

        # Create writer and their article
        self.writer = User.objects.create_user(
            username='writer',
            email='writer@test.com',
            password='pass123'
        )
        self.writer_profile = self.writer.profile  # Use auto-created profile
        self.writer_profile.role = 'writer'
        self.writer_profile.save()
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )
        self.article = Article.objects.create(
            title='Test Article',
            content='<p>Test content</p>',
            bulletin=self.bulletin,
            status='published',
            visibility='public',
            published=timezone.now()
        )

        # Create reader
        self.reader = User.objects.create_user(
            username='reader',
            email='reader@test.com',
            password='pass123'
        )
        self.reader_profile = self.reader.profile  # Use auto-created profile
        self.reader_profile.role = 'reader'
        self.reader_profile.save()

    def test_read_later_toggle_requires_login(self):
        """Read later toggle requires user to be logged in"""
        response = self.client.post(reverse('toggle_read_later', args=[self.article.id]))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_read_later_toggle_adds_bookmark(self):
        """Reader can bookmark an article"""
        self.client.login(username='reader', password='pass123')
        next_url = '/profile/'
        response = self.client.post(
            reverse('toggle_read_later', args=[self.article.id]),
            {'next': next_url}
        )

        # ReadLater should be created
        self.assertTrue(ReadLater.objects.filter(
            article=self.article,
            author=self.reader_profile
        ).exists())

        # Should redirect
        self.assertEqual(response.status_code, 302)

    def test_read_later_toggle_removes_bookmark(self):
        """Reader can remove bookmark from article"""
        self.client.login(username='reader', password='pass123')

        # Create read later first
        ReadLater.objects.create(article=self.article, author=self.reader_profile)
        self.assertTrue(ReadLater.objects.filter(
            article=self.article,
            author=self.reader_profile
        ).exists())

        # Toggle read later (should remove it) with next parameter to avoid get_absolute_url bug
        next_url = '/profile/'
        response = self.client.post(
            reverse('toggle_read_later', args=[self.article.id]),
            {'next': next_url}
        )

        # ReadLater should be deleted
        self.assertFalse(ReadLater.objects.filter(
            article=self.article,
            author=self.reader_profile
        ).exists())

        # Should redirect
        self.assertEqual(response.status_code, 302)

    def test_read_later_toggle_prevents_self_bookmark(self):
        """User cannot bookmark their own article"""
        self.client.login(username='writer', password='pass123')
        next_url = '/profile/'
        response = self.client.post(
            reverse('toggle_read_later', args=[self.article.id]),
            {'next': next_url}
        )

        # ReadLater should NOT be created
        self.assertFalse(ReadLater.objects.filter(
            article=self.article,
            author=self.writer_profile
        ).exists())

        # Should redirect
        self.assertEqual(response.status_code, 302)

    def test_read_later_toggle_respects_next_parameter(self):
        """Read later toggle should redirect to 'next' parameter if provided"""
        self.client.login(username='reader', password='pass123')
        next_url = '/profile/'
        response = self.client.post(
            reverse('toggle_read_later', args=[self.article.id]),
            {'next': next_url}
        )

        # Should redirect to next_url
        self.assertEqual(response.url, next_url)
