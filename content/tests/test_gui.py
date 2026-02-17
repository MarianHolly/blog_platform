from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from content.models import Article, Bulletin


class GuiPageLoadTests(TestCase):
    """Test that key pages load without errors using Django Client"""

    def setUp(self):
        self.client = Client()

    def test_homepage_loads(self):
        """Homepage should load without errors"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Blog Platform', response.content.decode())

    def test_about_page_loads(self):
        """About page should load without errors"""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_qa_page_loads(self):
        """Q&A page should load without errors"""
        response = self.client.get(reverse('qa'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_loads(self):
        """Signup page should display form"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_login_page_loads(self):
        """Login page should display form"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_articles_list_page_loads(self):
        """Articles list page should load"""
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)


class GuiFormSubmissionTests(TestCase):
    """Test form submissions and page interactions using Django Client"""

    def setUp(self):
        self.client = Client()
        # Create test writer and article for viewing
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

    def test_signup_form_submission(self):
        """User can submit signup form and create account"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123'
        })

        # Should redirect to login
        self.assertEqual(response.status_code, 302)

        # User should be created
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_form_submission(self):
        """User can submit login form and authenticate"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        user.profile.role = 'reader'  # Use auto-created profile

        user.profile.save()

        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass123'
        })

        # Should redirect to profile
        self.assertEqual(response.status_code, 302)
        self.assertIn('profile', response.url)

    def test_article_detail_page_displays(self):
        """Article detail page displays content"""
        response = self.client.get(
            reverse('article_detail', args=[self.article.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')
        # Content is displayed (may be sanitized by bleach)
        self.assertIn(b'article-content', response.content)

    def test_bulletin_detail_page_displays(self):
        """Bulletin detail page displays articles"""
        response = self.client.get(
            reverse('bulletin_detail', args=[self.bulletin.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Bulletin')
        self.assertContains(response, 'Test Article')

    def test_search_form_submission(self):
        """Search form can be submitted and returns results"""
        response = self.client.get(reverse('article_search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        # Search should find the article
        self.assertContains(response, 'Test Article')

    def test_search_no_results(self):
        """Search with no matching results displays correctly"""
        response = self.client.get(
            reverse('article_search'),
            {'q': 'nonexistentArticleKeyword'}
        )
        self.assertEqual(response.status_code, 200)


class GuiNavigationTests(TestCase):
    """Test navigation and page routing using Django Client"""

    def setUp(self):
        self.client = Client()
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        self.profile = self.user.profile  # Use auto-created profile

        self.profile.role = 'reader'

        self.profile.save()

    def test_profile_page_accessible(self):
        """User profile page is accessible"""
        response = self.client.get(
            reverse('profile', kwargs={'username': 'testuser'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_authenticated_user_can_access_profile(self):
        """Authenticated user sees own profile"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(
            reverse('profile', kwargs={'username': 'testuser'})
        )
        self.assertEqual(response.status_code, 200)
        # Profile page should have toggle buttons for own profile
        self.assertTrue(response.context.get('show_toggle_buttons'))

    def test_redirect_from_authenticated_login_page(self):
        """Authenticated user gets redirected from login page"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(reverse('login'))
        # Should redirect (redirect_authenticated_user = True)
        self.assertEqual(response.status_code, 302)

    def test_article_not_found_returns_404(self):
        """Nonexistent article returns 404"""
        response = self.client.get(
            reverse('article_detail', args=[99999])
        )
        self.assertEqual(response.status_code, 404)

    def test_bulletin_not_found_returns_404(self):
        """Nonexistent bulletin returns 404"""
        response = self.client.get(
            reverse('bulletin_detail', args=['nonexistent-bulletin'])
        )
        self.assertEqual(response.status_code, 404)

