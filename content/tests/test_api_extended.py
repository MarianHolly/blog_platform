from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import Profile
from content.models import Article, Bulletin, Subscription


class ArticleValidationTestCase(TestCase):
    """
    Test Article API validation and edge cases.

    Tests input validation, error responses, and edge cases.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        self.writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        self.writer_profile = Profile.objects.create(user=self.writer_user, role='writer')

        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

    def test_create_article_missing_required_fields(self):
        """Creating article without required fields should fail."""
        self.client.force_authenticate(user=self.writer_user)

        # Missing title
        response = self.client.post('/api/v1/articles/', {
            'content': 'Some content',
            'status': 'draft'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing content
        response = self.client.post('/api/v1/articles/', {
            'title': 'Test Title',
            'status': 'draft'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_invalid_status(self):
        """Creating article with invalid status should fail."""
        self.client.force_authenticate(user=self.writer_user)

        response = self.client.post('/api/v1/articles/', {
            'title': 'Test',
            'content': 'Content',
            'status': 'invalid_status',
            'visibility': 'public'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_invalid_visibility(self):
        """Creating article with invalid visibility should fail."""
        self.client.force_authenticate(user=self.writer_user)

        response = self.client.post('/api/v1/articles/', {
            'title': 'Test',
            'content': 'Content',
            'status': 'draft',
            'visibility': 'invalid_visibility'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_article_as_reader(self):
        """Readers cannot create articles."""
        reader_user = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        Profile.objects.create(user=reader_user, role='reader')

        self.client.force_authenticate(user=reader_user)

        response = self.client.post('/api/v1/articles/', {
            'title': 'Test',
            'content': 'Content',
            'status': 'draft',
            'visibility': 'public'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_slug_auto_generation(self):
        """Slug should be auto-generated from title."""
        self.client.force_authenticate(user=self.writer_user)

        response = self.client.post('/api/v1/articles/', {
            'title': 'My Test Article Title',
            'content': 'Content',
            'status': 'draft',
            'visibility': 'public'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        article = Article.objects.get(id=response.data['id'])
        self.assertTrue(article.slug.startswith('my-test-article-title'))


class ArticleFilteringTestCase(TestCase):
    """
    Test Article API filtering and ordering.

    Tests complex queries and combinations.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        self.writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        self.writer_profile = Profile.objects.create(user=self.writer_user, role='writer')

        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Tech Bulletin',
            slug='tech-bulletin'
        )

        # Create multiple articles with different attributes
        self.article1 = Article.objects.create(
            bulletin=self.bulletin,
            title='Python Tutorial',
            slug='python-tutorial',
            content='Learn Python',
            status='published',
            visibility='public'
        )

        self.article2 = Article.objects.create(
            bulletin=self.bulletin,
            title='Django Guide',
            slug='django-guide',
            content='Learn Django',
            status='published',
            visibility='private'
        )

        self.article3 = Article.objects.create(
            bulletin=self.bulletin,
            title='Draft Article',
            slug='draft-article',
            content='Draft content',
            status='draft',
            visibility='public'
        )

    def test_filter_by_bulletin(self):
        """Test filtering articles by bulletin slug."""
        response = self.client.get(f'/api/v1/articles/?bulletin={self.bulletin.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Anonymous users should only see public published articles
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_visibility(self):
        """Test filtering articles by visibility."""
        self.client.force_authenticate(user=self.writer_user)

        response = self.client.get('/api/v1/articles/?visibility=public')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see public articles (published + draft for owner)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_ordering_by_created(self):
        """Test ordering articles by creation date."""
        response = self.client.get('/api/v1/articles/?ordering=-created')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results should be ordered by newest first

    def test_ordering_by_title(self):
        """Test ordering articles by title."""
        response = self.client.get('/api/v1/articles/?ordering=title')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_combined_filters(self):
        """Test combining multiple filters."""
        self.client.force_authenticate(user=self.writer_user)

        response = self.client.get(
            f'/api/v1/articles/?status=published&visibility=public&ordering=-created'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ArticlePaginationTestCase(TestCase):
    """
    Test Article API pagination.

    Tests pagination, page size, and navigation.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        writer_profile = Profile.objects.create(user=writer_user, role='writer')

        bulletin = Bulletin.objects.create(
            owner=writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

        # Create 25 articles for pagination testing
        for i in range(25):
            Article.objects.create(
                bulletin=bulletin,
                title=f'Article {i}',
                slug=f'article-{i}',
                content=f'Content {i}',
                status='published',
                visibility='public'
            )

    def test_default_pagination(self):
        """Test default pagination (20 items per page)."""
        response = self.client.get('/api/v1/articles/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 20)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_pagination_second_page(self):
        """Test navigating to second page."""
        response = self.client.get('/api/v1/articles/?page=2')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_custom_page_size(self):
        """Test custom page size parameter."""
        response = self.client.get('/api/v1/articles/?page_size=10')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_invalid_page_number(self):
        """Test requesting invalid page number."""
        response = self.client.get('/api/v1/articles/?page=999')

        # Should return 404 or empty results
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK])


class PrivateArticleAccessTestCase(TestCase):
    """
    Test access control for private articles.

    Tests subscription-based access to private content.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create writer and bulletin
        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        self.writer_profile = Profile.objects.create(user=writer_user, role='writer')

        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Premium Bulletin',
            slug='premium-bulletin'
        )

        # Create private article
        self.private_article = Article.objects.create(
            bulletin=self.bulletin,
            title='Premium Content',
            slug='premium-content',
            content='Subscriber-only content',
            status='published',
            visibility='private'
        )

        # Create reader (not subscribed)
        self.reader_user = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.reader_profile = Profile.objects.create(user=self.reader_user, role='reader')

        # Create subscribed reader
        self.subscriber_user = User.objects.create_user('subscriber', 'sub@test.com', 'pass123')
        self.subscriber_profile = Profile.objects.create(user=self.subscriber_user, role='reader')
        Subscription.objects.create(subscriber=self.subscriber_profile, bulletin=self.bulletin)

    def test_anonymous_cannot_see_private_article_in_list(self):
        """Anonymous users should not see private articles in list."""
        response = self.client.get('/api/v1/articles/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_anonymous_cannot_access_private_article_detail(self):
        """Anonymous users should not access private article details."""
        response = self.client.get(f'/api/v1/articles/{self.private_article.slug}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_subscriber_cannot_see_private_article(self):
        """Non-subscribed readers should not see private articles."""
        self.client.force_authenticate(user=self.reader_user)

        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.data['count'], 0)

        # Direct access should also fail
        response = self.client.get(f'/api/v1/articles/{self.private_article.slug}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscriber_can_see_private_article(self):
        """Subscribed readers should see private articles."""
        self.client.force_authenticate(user=self.subscriber_user)

        # Should appear in list
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.data['count'], 1)

        # Should access detail
        response = self.client.get(f'/api/v1/articles/{self.private_article.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_writer_can_see_own_private_article(self):
        """Writers should see their own private articles."""
        writer_user = self.writer_profile.user
        self.client.force_authenticate(user=writer_user)

        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.data['count'], 1)


class CommentValidationTestCase(TestCase):
    """
    Test Comment API validation and edge cases.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create user and article
        self.user = User.objects.create_user('user', 'user@test.com', 'pass123')
        self.profile = Profile.objects.create(user=self.user, role='reader')

        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        writer_profile = Profile.objects.create(user=writer_user, role='writer')

        bulletin = Bulletin.objects.create(
            owner=writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

        self.article = Article.objects.create(
            bulletin=bulletin,
            title='Test Article',
            slug='test-article',
            content='Content',
            status='published',
            visibility='public'
        )

    def test_create_comment_on_nonexistent_article(self):
        """Creating comment on non-existent article should fail."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/v1/comments/', {
            'article': 99999,
            'content': 'Test comment'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_comment_empty_content(self):
        """Creating comment with empty content should fail."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/v1/comments/', {
            'article': self.article.id,
            'content': ''
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_comment_missing_article(self):
        """Creating comment without article should fail."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/v1/comments/', {
            'content': 'Test comment'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BulletinSubscriptionEdgeCasesTestCase(TestCase):
    """
    Test Bulletin subscription edge cases.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create writer and bulletin
        self.writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        self.writer_profile = Profile.objects.create(user=self.writer_user, role='writer')

        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

        # Create reader
        self.reader_user = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.reader_profile = Profile.objects.create(user=self.reader_user, role='reader')

    def test_subscribe_to_own_bulletin(self):
        """Writers cannot subscribe to their own bulletin."""
        self.client.force_authenticate(user=self.writer_user)

        response = self.client.post(f'/api/v1/bulletins/{self.bulletin.slug}/subscribe/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_to_nonexistent_bulletin(self):
        """Subscribing to non-existent bulletin should fail."""
        self.client.force_authenticate(user=self.reader_user)

        response = self.client.post('/api/v1/bulletins/nonexistent/subscribe/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscribe_without_authentication(self):
        """Anonymous users cannot subscribe."""
        response = self.client.post(f'/api/v1/bulletins/{self.bulletin.slug}/subscribe/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
