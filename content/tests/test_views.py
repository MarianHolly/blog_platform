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


class ArticleCreateViewTest(TestCase):
    """Test ArticleCreateView functionality and permissions"""

    def setUp(self):
        """Set up test data"""
        # Create a writer user
        self.writer_user = User.objects.create_user(
            username='writer',
            email='writer@test.com',
            password='Password123'
        )
        self.writer_profile = Profile.objects.create(
            user=self.writer_user,
            role='writer'
        )
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Writer Bulletin',
            slug='writer-bulletin'
        )

        # Create a reader user
        self.reader_user = User.objects.create_user(
            username='reader',
            email='reader@test.com',
            password='Password123'
        )
        self.reader_profile = Profile.objects.create(
            user=self.reader_user,
            role='reader'
        )

        self.client = Client()

    def test_create_article_form_display(self):
        """Test that article create form displays for writers"""
        self.client.login(username='writer', password='Password123')
        url = reverse('article_create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTemplateUsed(response, 'content/form.html')

    def test_create_article_with_valid_data(self):
        """Test successful article creation"""
        self.client.login(username='writer', password='Password123')
        url = reverse('article_create')

        data = {
            'title': 'New Article',
            'status': 'draft',
            'visibility': 'private',
            'content': '<p>This is article content</p>'
        }

        response = self.client.post(url, data)

        # Should redirect (302)
        self.assertEqual(response.status_code, 302)
        # Should redirect to bulletin detail page
        self.assertIn('/bulletin/', response.url)

        # Article should be created
        article = Article.objects.filter(title='New Article').first()
        self.assertIsNotNone(article)
        self.assertEqual(article.bulletin, self.bulletin)
        self.assertEqual(article.status, 'draft')

    def test_create_article_without_content(self):
        """Test that article creation fails without content"""
        self.client.login(username='writer', password='Password123')
        url = reverse('article_create')

        data = {
            'title': 'Empty Article',
            'status': 'draft',
            'visibility': 'private',
            'content': ''
        }

        response = self.client.post(url, data)

        # Should not redirect (form is invalid)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

        # Article should not be created
        self.assertFalse(Article.objects.filter(title='Empty Article').exists())

    def test_reader_cannot_create_article(self):
        """Test that readers cannot create articles"""
        self.client.login(username='reader', password='Password123')
        url = reverse('article_create')
        response = self.client.get(url)

        # Should get 403 Forbidden (WriterRequiredMixin enforces this)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_create_article(self):
        """Test that anonymous users cannot create articles"""
        url = reverse('article_create')
        response = self.client.get(url)

        # Should redirect to login (LoginRequiredMixin)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_article_assigned_to_user_bulletin(self):
        """Test that article is automatically assigned to user's bulletin"""
        self.client.login(username='writer', password='Password123')
        url = reverse('article_create')

        data = {
            'title': 'Bulletin Article',
            'status': 'published',
            'visibility': 'public',
            'content': '<p>Test content</p>'
        }

        self.client.post(url, data)

        article = Article.objects.get(title='Bulletin Article')
        self.assertEqual(article.bulletin, self.writer_profile.bulletin)


class ArticleUpdateViewExtendedTest(TestCase):
    """Extended tests for ArticleUpdateView"""

    def setUp(self):
        """Set up test data"""
        # Create writer
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
            title='Writer Bulletin',
            slug='writer-bulletin'
        )

        # Create article
        self.article = Article.objects.create(
            title='Original Title',
            status='draft',
            visibility='private',
            bulletin=self.bulletin,
            content='<p>Original content</p>'
        )

        self.client = Client()

    def test_update_article_form_display(self):
        """Test that update form displays for article owner"""
        self.client.login(username='writer', password='Password123')
        url = reverse('article_edit', kwargs={'pk': self.article.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.article)

    def test_update_article_with_valid_data(self):
        """Test successful article update"""
        self.client.login(username='writer', password='Password123')
        url = reverse('article_edit', kwargs={'pk': self.article.id})

        data = {
            'title': 'Updated Title',
            'status': 'published',
            'visibility': 'public',
            'content': '<p>Updated content</p>'
        }

        response = self.client.post(url, data)

        # Should redirect (302)
        self.assertEqual(response.status_code, 302)
        # Should redirect to article detail page
        self.assertIn('/article/', response.url)

        # Article should be updated
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Updated Title')
        self.assertEqual(self.article.status, 'published')

    def test_update_article_without_content(self):
        """Test that article update fails without content"""
        self.client.login(username='writer', password='Password123')
        url = reverse('article_edit', kwargs={'pk': self.article.id})

        data = {
            'title': 'Updated Title',
            'status': 'draft',
            'visibility': 'private',
            'content': ''
        }

        response = self.client.post(url, data)

        # Should not redirect (form is invalid)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

        # Title should not be updated
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Original Title')


class ArticleDeleteViewExtendedTest(TestCase):
    """Extended tests for ArticleDeleteView"""

    def setUp(self):
        """Set up test data"""
        # Create writer
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
            title='Writer Bulletin',
            slug='writer-bulletin'
        )

        # Create another writer to test access control
        self.other_writer_user = User.objects.create_user(
            username='other_writer',
            password='Password123'
        )
        self.other_writer_profile = Profile.objects.create(
            user=self.other_writer_user,
            role='writer'
        )
        self.other_bulletin = Bulletin.objects.create(
            owner=self.other_writer_profile,
            title='Other Bulletin',
            slug='other-bulletin'
        )

        # Create articles
        self.article = Article.objects.create(
            title='Article to Delete',
            status='draft',
            visibility='private',
            bulletin=self.bulletin
        )

        self.other_article = Article.objects.create(
            title='Other Article',
            status='draft',
            visibility='private',
            bulletin=self.other_bulletin
        )

        self.client = Client()

    def test_delete_confirmation_page_displays(self):
        """Test that delete confirmation page displays"""
        self.client.login(username='writer', password='Password123')
        url = reverse('article_delete', kwargs={'pk': self.article.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/confirm_delete.html')

    def test_owner_can_delete_article(self):
        """Test that article owner can delete their article"""
        self.client.login(username='writer', password='Password123')
        article_id = self.article.id

        url = reverse('article_delete', kwargs={'pk': article_id})
        response = self.client.post(url)

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Article should be deleted
        self.assertFalse(Article.objects.filter(id=article_id).exists())

    def test_non_owner_cannot_delete_article(self):
        """Test that non-owner gets 403 when trying to delete"""
        self.client.login(username='other_writer', password='Password123')
        url = reverse('article_delete', kwargs={'pk': self.article.id})
        response = self.client.get(url)

        # Should get 403 Forbidden
        self.assertEqual(response.status_code, 403)

        # Article should still exist
        self.assertTrue(Article.objects.filter(id=self.article.id).exists())

    def test_anonymous_cannot_delete_article(self):
        """Test that anonymous users cannot delete articles"""
        url = reverse('article_delete', kwargs={'pk': self.article.id})
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class ArticleEvaluationViewTest(TestCase):
    """Test ArticleEvaluationView functionality"""

    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='Password123'
        )
        self.admin_profile = Profile.objects.create(
            user=self.admin_user,
            role='admin'
        )

        # Create writer user
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
            title='Writer Bulletin',
            slug='writer-bulletin'
        )

        # Create articles with different evaluation statuses
        self.pending_article = Article.objects.create(
            title='Pending Article',
            status='published',
            visibility='public',
            bulletin=self.bulletin,
            evaluation='pending'
        )

        self.under_review_article = Article.objects.create(
            title='Under Review Article',
            status='published',
            visibility='public',
            bulletin=self.bulletin,
            evaluation='under_review'
        )

        self.approved_article = Article.objects.create(
            title='Approved Article',
            status='published',
            visibility='public',
            bulletin=self.bulletin,
            evaluation='approved'
        )

        self.client = Client()

    def test_evaluation_toggle_form_display(self):
        """Test that evaluation form displays for admins"""
        self.client.login(username='admin', password='Password123')
        url = reverse('article_evaluation_decision', kwargs={'id': self.under_review_article.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTemplateUsed(response, 'accounts/evaluation_form.html')

    def test_admin_can_approve_article(self):
        """Test that admin can approve an article"""
        self.client.login(username='admin', password='Password123')
        url = reverse('article_evaluation_decision', kwargs={'id': self.under_review_article.id})

        data = {
            'evaluation': 'approved'
        }

        response = self.client.post(url, data)

        # Should redirect (302)
        self.assertEqual(response.status_code, 302)
        # Should redirect to evaluation dashboard
        self.assertIn('/evaluate/dashboard/', response.url)

        # Article should be approved
        self.under_review_article.refresh_from_db()
        self.assertEqual(self.under_review_article.evaluation, 'approved')

    def test_admin_can_reject_article(self):
        """Test that admin can reject an article"""
        self.client.login(username='admin', password='Password123')
        url = reverse('article_evaluation_decision', kwargs={'id': self.under_review_article.id})

        data = {
            'evaluation': 'rejected'
        }

        response = self.client.post(url, data)

        # Should redirect to evaluation dashboard
        self.assertEqual(response.status_code, 302)

        # Article should be rejected
        self.under_review_article.refresh_from_db()
        self.assertEqual(self.under_review_article.evaluation, 'rejected')

    def test_non_admin_cannot_evaluate(self):
        """Test that non-admin users cannot evaluate articles"""
        self.client.login(username='writer', password='Password123')
        url = reverse('article_evaluation_decision', kwargs={'id': self.under_review_article.id})
        response = self.client.get(url)

        # Should get 403 Forbidden (AdministratorRequiredMixin enforces this)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_evaluate(self):
        """Test that anonymous users cannot evaluate articles"""
        url = reverse('article_evaluation_decision', kwargs={'id': self.under_review_article.id})
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_evaluation_toggle_pending_to_under_review(self):
        """Test moving article from pending to under_review"""
        self.client.login(username='admin', password='Password123')
        url = reverse('article_evaluation_toggle', kwargs={'id': self.pending_article.id})

        response = self.client.post(url)

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Article should be under_review
        self.pending_article.refresh_from_db()
        self.assertEqual(self.pending_article.evaluation, 'under_review')

    def test_evaluation_nonexistent_article(self):
        """Test evaluation of non-existent article returns 404"""
        self.client.login(username='admin', password='Password123')
        url = reverse('article_evaluation_decision', kwargs={'id': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
