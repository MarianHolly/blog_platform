from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import Profile
from content.models import Article, Bulletin, Subscription
from engagement.models import Like, ReadLater


class ArticleAPITestCase(TestCase):
    """
    Test Article API endpoints.

    Tests: List, create, retrieve, update, delete, like, bookmark.
    Permissions: Anonymous read, authenticated write, owner-only edit/delete.
    """

    def setUp(self):
        """Set up test data before each test method."""
        self.client = APIClient()

        # Create reader user with profile
        self.reader_user = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.reader_profile = Profile.objects.create(user=self.reader_user, role='reader')

        # Create writer user with profile
        self.writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        self.writer_profile = Profile.objects.create(user=self.writer_user, role='writer')

        # Create bulletin for writer
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Test Bulletin',
            slug='test-bulletin',
            description='Test description'
        )

        # Create published public article
        self.public_article = Article.objects.create(
            bulletin=self.bulletin,
            title='Public Article',
            slug='public-article',
            content='Public content',
            status='published',
            visibility='public'
        )

        # Create published private article
        self.private_article = Article.objects.create(
            bulletin=self.bulletin,
            title='Private Article',
            slug='private-article',
            content='Private content',
            status='published',
            visibility='private'
        )

        # Create draft article
        self.draft_article = Article.objects.create(
            bulletin=self.bulletin,
            title='Draft Article',
            slug='draft-article',
            content='Draft content',
            status='draft',
            visibility='public'
        )

    def test_list_articles_anonymous(self):
        """Anonymous users should only see published public articles."""
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should see only the public article
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['slug'], 'public-article')

    def test_list_articles_authenticated_reader(self):
        """Authenticated readers should see public articles."""
        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get('/api/v1/articles/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Reader sees only public article (not subscribed to private)
        self.assertEqual(response.data['count'], 1)

    def test_list_articles_with_subscription(self):
        """Readers subscribed to bulletin should see private articles."""
        # Create subscription
        Subscription.objects.create(
            subscriber=self.reader_profile,
            bulletin=self.bulletin
        )

        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get('/api/v1/articles/')

        # Reader should now see both public and private articles
        self.assertEqual(response.data['count'], 2)

    def test_retrieve_article(self):
        """Test retrieving single article detail."""
        response = self.client.get(f'/api/v1/articles/{self.public_article.slug}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Public Article')
        self.assertIn('content', response.data)  # Detail includes content

    def test_create_article_unauthorized(self):
        """Anonymous users cannot create articles."""
        article_data = {
            'title': 'New Article',
            'content': 'New content',
            'status': 'draft'
        }
        response = self.client.post('/api/v1/articles/', article_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_article_as_writer(self):
        """Writers can create articles."""
        self.client.force_authenticate(user=self.writer_user)

        article_data = {
            'title': 'New Article',
            'content': 'New content',
            'status': 'draft',
            'visibility': 'public'
        }
        response = self.client.post('/api/v1/articles/', article_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.filter(title='New Article').count(), 1)

    def test_update_article_owner(self):
        """Article owner can update their article."""
        self.client.force_authenticate(user=self.writer_user)

        update_data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'status': 'published',
            'visibility': 'public'
        }
        response = self.client.put(
            f'/api/v1/articles/{self.draft_article.slug}/',
            update_data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.draft_article.refresh_from_db()
        self.assertEqual(self.draft_article.title, 'Updated Title')

    def test_update_article_non_owner(self):
        """Non-owners cannot update articles."""
        self.client.force_authenticate(user=self.reader_user)

        update_data = {'title': 'Hacked Title'}
        response = self.client.patch(
            f'/api/v1/articles/{self.public_article.slug}/',
            update_data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_article_owner(self):
        """Article owner can delete their article."""
        self.client.force_authenticate(user=self.writer_user)

        response = self.client.delete(f'/api/v1/articles/{self.draft_article.slug}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Article.objects.filter(slug='draft-article').exists())

    def test_like_article(self):
        """Authenticated users can like articles."""
        self.client.force_authenticate(user=self.reader_user)

        response = self.client.post(f'/api/v1/articles/{self.public_article.slug}/like/')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'liked')
        self.assertTrue(
            Like.objects.filter(
                author=self.reader_profile,
                article=self.public_article
            ).exists()
        )

    def test_unlike_article(self):
        """Liking an already-liked article should unlike it."""
        # Create initial like
        Like.objects.create(author=self.reader_profile, article=self.public_article)

        self.client.force_authenticate(user=self.reader_user)
        response = self.client.post(f'/api/v1/articles/{self.public_article.slug}/like/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unliked')
        self.assertFalse(
            Like.objects.filter(
                author=self.reader_profile,
                article=self.public_article
            ).exists()
        )

    def test_bookmark_article(self):
        """Authenticated users can bookmark articles."""
        self.client.force_authenticate(user=self.reader_user)

        response = self.client.post(f'/api/v1/articles/{self.public_article.slug}/bookmark/')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'bookmarked')
        self.assertTrue(
            ReadLater.objects.filter(
                author=self.reader_profile,
                article=self.public_article
            ).exists()
        )

    def test_search_articles(self):
        """Test article search functionality."""
        response = self.client.get('/api/v1/articles/?search=Public')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['slug'], 'public-article')

    def test_filter_articles_by_status(self):
        """Test filtering articles by status."""
        self.client.force_authenticate(user=self.writer_user)

        response = self.client.get('/api/v1/articles/?status=draft')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Writer should see their draft article
        self.assertGreater(response.data['count'], 0)


class BulletinAPITestCase(TestCase):
    """
    Test Bulletin API endpoints.

    Tests: List, retrieve, subscribe.
    Note: Bulletins are read-only (created automatically for writers).
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create reader with profile
        self.reader_user = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.reader_profile = Profile.objects.create(user=self.reader_user, role='reader')

        # Create writer with profile and bulletin
        self.writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        self.writer_profile = Profile.objects.create(user=self.writer_user, role='writer')

        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Test Bulletin',
            slug='test-bulletin',
            description='Test description'
        )

    def test_list_bulletins(self):
        """Anyone can list bulletins."""
        response = self.client.get('/api/v1/bulletins/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_bulletin(self):
        """Anyone can retrieve bulletin details."""
        response = self.client.get(f'/api/v1/bulletins/{self.bulletin.slug}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Bulletin')

    def test_subscribe_to_bulletin(self):
        """Readers can subscribe to bulletins."""
        self.client.force_authenticate(user=self.reader_user)

        response = self.client.post(f'/api/v1/bulletins/{self.bulletin.slug}/subscribe/')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'subscribed')
        self.assertTrue(
            Subscription.objects.filter(
                subscriber=self.reader_profile,
                bulletin=self.bulletin
            ).exists()
        )

    def test_unsubscribe_from_bulletin(self):
        """Subscribing again should unsubscribe."""
        Subscription.objects.create(subscriber=self.reader_profile, bulletin=self.bulletin)

        self.client.force_authenticate(user=self.reader_user)
        response = self.client.post(f'/api/v1/bulletins/{self.bulletin.slug}/subscribe/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unsubscribed')

    def test_writer_cannot_subscribe(self):
        """Writers cannot subscribe to bulletins."""
        self.client.force_authenticate(user=self.writer_user)

        response = self.client.post(f'/api/v1/bulletins/{self.bulletin.slug}/subscribe/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SubscriptionAPITestCase(TestCase):
    """
    Test Subscription API endpoints.

    Tests: List user subscriptions, create, delete.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        self.user = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.profile = Profile.objects.create(user=self.user, role='reader')

        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        writer_profile = Profile.objects.create(user=writer_user, role='writer')

        self.bulletin = Bulletin.objects.create(
            owner=writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

    def test_list_subscriptions_unauthorized(self):
        """Anonymous users cannot list subscriptions."""
        response = self.client.get('/api/v1/subscriptions/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_subscriptions(self):
        """Users can list their subscriptions."""
        Subscription.objects.create(subscriber=self.profile, bulletin=self.bulletin)

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/subscriptions/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_subscription(self):
        """Users can create subscriptions."""
        self.client.force_authenticate(user=self.user)

        subscription_data = {'bulletin_id': self.bulletin.id}
        response = self.client.post('/api/v1/subscriptions/', subscription_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Subscription.objects.filter(
                subscriber=self.profile,
                bulletin=self.bulletin
            ).exists()
        )
