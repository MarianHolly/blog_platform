from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from content.models import Article, Bulletin


class ArticleUpdateViewPermissionTest(TestCase):
    """Test ArticleUpdateView permissions and ownership enforcement"""

    def setUp(self):
        """Set up test data: two writers with articles"""
        # Create Writer 1
        self.writer1_user = User.objects.create_user(
            username='writer1',
            password='Password123'
        )
        self.writer1_profile = Profile.objects.create(
            user=self.writer1_user,
            role='writer'
        )
        self.bulletin1 = Bulletin.objects.create(
            owner=self.writer1_profile,
            title='Writer 1 Bulletin',
            slug='writer1-bulletin'
        )
        self.article1 = Article.objects.create(
            title='Writer 1 Article',
            status='draft',
            visibility='private',
            bulletin=self.bulletin1
        )

        # Create Writer 2
        self.writer2_user = User.objects.create_user(
            username='writer2',
            password='Password456'
        )
        self.writer2_profile = Profile.objects.create(
            user=self.writer2_user,
            role='writer'
        )
        self.bulletin2 = Bulletin.objects.create(
            owner=self.writer2_profile,
            title='Writer 2 Bulletin',
            slug='writer2-bulletin'
        )
        self.article2 = Article.objects.create(
            title='Writer 2 Article',
            status='draft',
            visibility='private',
            bulletin=self.bulletin2
        )

        self.client = Client()

    def test_owner_can_edit_own_article(self):
        """Test that article owner can edit their own article"""
        self.client.login(username='writer1', password='Password123')
        url = reverse('article_edit', kwargs={'pk': self.article1.id})
        response = self.client.get(url)

        # Should get 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_non_owner_cannot_edit_article(self):
        """Test that non-owner gets 403 Forbidden when trying to edit"""
        self.client.login(username='writer2', password='Password456')
        url = reverse('article_edit', kwargs={'pk': self.article1.id})
        response = self.client.get(url)

        # Should get 403 Forbidden (ArticleOwnerMixin enforces this)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_edit_article(self):
        """Test that anonymous users cannot edit articles"""
        url = reverse('article_edit', kwargs={'pk': self.article1.id})
        response = self.client.get(url)

        # Should redirect to login (LoginRequiredMixin)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class ArticleDeleteViewRedirectTest(TestCase):
    """Test ArticleDeleteView redirect behavior"""

    def setUp(self):
        """Set up test data"""
        self.writer_user = User.objects.create_user(
            username='writer',
            password='Password123'
        )
        self.writer_profile = Profile.objects.create(
            user=self.writer_user,
            role='writer'
        )
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )
        self.article = Article.objects.create(
            title='Test Article',
            status='draft',
            visibility='private',
            bulletin=self.bulletin
        )

        self.client = Client()

    def test_article_delete_redirects_to_bulletin_owner_profile(self):
        """Test that article deletion redirects to bulletin owner's profile"""
        self.client.login(username='writer', password='Password123')
        article_id = self.article.id

        # Delete article via POST
        delete_url = reverse('article_delete', kwargs={'pk': article_id})
        response = self.client.post(delete_url)

        # Should redirect (302) to bulletin owner's profile
        self.assertEqual(response.status_code, 302)

        # Check redirect URL contains the owner's username
        expected_url = reverse('profile', kwargs={'username': self.writer_user.username})
        self.assertEqual(response.url, expected_url)

    def test_deleted_article_no_longer_exists(self):
        """Test that article is actually deleted from database"""
        self.client.login(username='writer', password='Password123')
        article_id = self.article.id

        # Verify article exists before deletion
        self.assertTrue(Article.objects.filter(id=article_id).exists())

        # Delete article
        delete_url = reverse('article_delete', kwargs={'pk': article_id})
        self.client.post(delete_url)

        # Verify article no longer exists
        self.assertFalse(Article.objects.filter(id=article_id).exists())

    def test_delete_response_is_accessible(self):
        """Test that redirect target (profile page) is accessible"""
        self.client.login(username='writer', password='Password123')

        # Delete article
        delete_url = reverse('article_delete', kwargs={'pk': self.article.id})
        response = self.client.post(delete_url, follow=True)

        # Follow redirect and verify we get 200 OK on profile page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.writer_user.username)


class BulletinDetailViewTest(TestCase):
    """Test bulletin detail page"""

    @classmethod
    def setUpTestData(cls):
        cls.writer = User.objects.create_user(
            username='writer', email='writer@test.com', password='pass123'
        )
        cls.writer_profile = Profile.objects.create(user=cls.writer, role='writer')
        cls.bulletin = Bulletin.objects.create(
            owner=cls.writer_profile, title='My Bulletin', slug='my-bulletin'
        )
        cls.article1 = Article.objects.create(
            title='Published Article',
            bulletin=cls.bulletin,
            status='published',
            visibility='public',
            published=timezone.now()
        )
        cls.article2 = Article.objects.create(
            title='Draft Article',
            bulletin=cls.bulletin,
            status='draft',
            visibility='private'
        )

    def test_bulletin_detail_loads(self):
        """Bulletin detail page should load"""
        response = self.client.get(reverse('bulletin_detail', args=[self.bulletin.slug]))
        self.assertEqual(response.status_code, 200)

    def test_bulletin_detail_shows_only_published_articles(self):
        """Bulletin detail should only show published articles"""
        response = self.client.get(reverse('bulletin_detail', args=[self.bulletin.slug]))
        self.assertContains(response, 'Published Article')
        self.assertNotContains(response, 'Draft Article')

    def test_bulletin_not_found(self):
        """Non-existent bulletin should return 404"""
        response = self.client.get(reverse('bulletin_detail', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)


class ArticleSearchViewTest(TestCase):
    """Test article search functionality"""

    @classmethod
    def setUpTestData(cls):
        cls.writer = User.objects.create_user(
            username='writer', email='writer@test.com', password='pass123'
        )
        cls.writer_profile = Profile.objects.create(user=cls.writer, role='writer')
        cls.bulletin = Bulletin.objects.create(
            owner=cls.writer_profile, title='Test Bulletin', slug='test'
        )
        cls.article1 = Article.objects.create(
            title='Python Programming Guide',
            bulletin=cls.bulletin,
            status='published',
            visibility='public',
            published=timezone.now()
        )
        cls.article2 = Article.objects.create(
            title='Django Web Framework',
            bulletin=cls.bulletin,
            status='published',
            visibility='public',
            published=timezone.now()
        )

    def test_search_page_loads(self):
        """Search page should load"""
        response = self.client.get(reverse('article_search'))
        self.assertEqual(response.status_code, 200)

    def test_search_finds_articles_by_title(self):
        """Search should find articles by title"""
        response = self.client.get(reverse('article_search') + '?q=Python')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Programming Guide')

    def test_search_no_results(self):
        """Search with no results should return empty"""
        response = self.client.get(reverse('article_search') + '?q=NonexistentArticle')
        self.assertEqual(response.status_code, 200)
