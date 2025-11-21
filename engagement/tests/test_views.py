from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from content.models import Article, Bulletin
from engagement.models import Like, ReadLater, Comment


class LikeToggleViewTest(TestCase):
    """Test LikeToggleView for toggling likes on articles"""

    @classmethod
    def setUpTestData(cls):
        print('\nLikeToggleView - setting setUpTestData')
        
        # Create writer with article
        cls.writer_user = User.objects.create_user(
            username='writer', email='writer@test.com', password='pass123'
        )
        cls.writer_profile = Profile.objects.create(
            user=cls.writer_user, role='writer'
        )
        cls.bulletin = Bulletin.objects.create(
            owner=cls.writer_profile, title='Test Bulletin', slug='test-bulletin'
        )
        cls.article = Article.objects.create(
            title='Test Article',
            bulletin=cls.bulletin,
            status='published',
            visibility='public',
            published=timezone.now()
        )
        
        # Create reader
        cls.reader_user = User.objects.create_user(
            username='reader', email='reader@test.com', password='pass123'
        )
        cls.reader_profile = Profile.objects.create(
            user=cls.reader_user, role='reader'
        )

    def test_reader_can_toggle_like(self):
        """Reader should be able to add/remove likes"""
        self.client.login(username='reader', password='pass123')
        response = self.client.post(reverse('toggle_like', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertTrue(Like.objects.filter(article=self.article, author=self.reader_profile).exists())

    def test_reader_can_unlike_article(self):
        """Reader should be able to remove a like"""
        Like.objects.create(article=self.article, author=self.reader_profile)
        self.client.login(username='reader', password='pass123')
        response = self.client.post(reverse('toggle_like', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertFalse(Like.objects.filter(article=self.article, author=self.reader_profile).exists())

    def test_author_cannot_like_own_article(self):
        """Author should not be able to like their own article"""
        self.client.login(username='writer', password='pass123')
        response = self.client.post(reverse('toggle_like', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertFalse(Like.objects.filter(article=self.article, author=self.writer_profile).exists())

    def test_like_toggle_redirects_with_next_param(self):
        """Like toggle should respect 'next' parameter"""
        self.client.login(username='reader', password='pass123')
        next_url = '/article/'
        response = self.client.post(
            reverse('toggle_like', args=[self.article.id]),
            {'next': next_url}
        )
        self.assertEqual(response.status_code, 302)


class ReadLaterToggleViewTest(TestCase):
    """Test ReadLaterToggleView for bookmarking articles"""

    @classmethod
    def setUpTestData(cls):
        print('\nReadLaterToggleView - setting setUpTestData')
        
        # Create writer with article
        cls.writer_user = User.objects.create_user(
            username='writer', email='writer@test.com', password='pass123'
        )
        cls.writer_profile = Profile.objects.create(
            user=cls.writer_user, role='writer'
        )
        cls.bulletin = Bulletin.objects.create(
            owner=cls.writer_profile, title='Test Bulletin', slug='test-bulletin'
        )
        cls.article = Article.objects.create(
            title='Test Article',
            bulletin=cls.bulletin,
            status='published',
            visibility='public',
            published=timezone.now()
        )
        
        # Create reader
        cls.reader_user = User.objects.create_user(
            username='reader', email='reader@test.com', password='pass123'
        )
        cls.reader_profile = Profile.objects.create(
            user=cls.reader_user, role='reader'
        )

    def test_reader_can_bookmark_article(self):
        """Reader should be able to bookmark an article"""
        self.client.login(username='reader', password='pass123')
        response = self.client.post(reverse('toggle_read_later', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertTrue(ReadLater.objects.filter(article=self.article, author=self.reader_profile).exists())

    def test_reader_can_remove_bookmark(self):
        """Reader should be able to remove a bookmark"""
        ReadLater.objects.create(article=self.article, author=self.reader_profile)
        self.client.login(username='reader', password='pass123')
        response = self.client.post(reverse('toggle_read_later', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertFalse(ReadLater.objects.filter(article=self.article, author=self.reader_profile).exists())

    def test_author_cannot_bookmark_own_article(self):
        """Author should not be able to bookmark their own article"""
        self.client.login(username='writer', password='pass123')
        response = self.client.post(reverse('toggle_read_later', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertFalse(ReadLater.objects.filter(article=self.article, author=self.writer_profile).exists())

    def test_read_later_toggle_redirects_with_next_param(self):
        """Read later toggle should respect 'next' parameter"""
        self.client.login(username='reader', password='pass123')
        next_url = '/article/'
        response = self.client.post(
            reverse('toggle_read_later', args=[self.article.id]),
            {'next': next_url}
        )
        self.assertEqual(response.status_code, 302)
