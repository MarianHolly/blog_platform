from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import Profile
from content.models import Article, Bulletin
from engagement.models import Comment, ReadLater


class CommentAPITestCase(TestCase):
    """
    Test Comment API endpoints.

    Tests: List, create, retrieve, update, delete.
    Permissions: Authenticated users can comment, only owners can edit/delete.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'pass123')
        self.profile1 = Profile.objects.get(user=self.user1)

        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'pass123')
        self.profile2 = Profile.objects.get(user=self.user2)

        # Create writer with article
        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        writer_profile = Profile.objects.get(user=writer_user)
        writer_profile.role = 'writer'
        writer_profile.save()

        bulletin = Bulletin.objects.create(
            owner=writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

        self.article = Article.objects.create(
            bulletin=bulletin,
            title='Test Article',
            slug='test-article',
            content='Test content',
            status='published',
            visibility='public'
        )

        # Create comment from user1
        self.comment = Comment.objects.create(
            author=self.profile1,
            article=self.article,
            content='Test comment from user1'
        )

    def test_list_comments_unauthorized(self):
        """Anonymous users cannot list comments."""
        response = self.client.get('/api/v1/comments/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_comments(self):
        """Authenticated users can list comments."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/comments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_comments_by_article(self):
        """Test filtering comments by article."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/comments/?article={self.article.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['content'], 'Test comment from user1')

    def test_create_comment_unauthorized(self):
        """Anonymous users cannot create comments."""
        comment_data = {
            'article': self.article.id,
            'content': 'New comment'
        }
        response = self.client.post('/api/v1/comments/', comment_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment(self):
        """Authenticated users can create comments."""
        self.client.force_authenticate(user=self.user2)

        comment_data = {
            'article': self.article.id,
            'content': 'New comment from user2'
        }
        response = self.client.post('/api/v1/comments/', comment_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Comment.objects.filter(
                author=self.profile2,
                content='New comment from user2'
            ).count(),
            1
        )

    def test_retrieve_comment(self):
        """Test retrieving single comment."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/comments/{self.comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test comment from user1')
        self.assertEqual(response.data['can_edit'], True)  # Owner can edit

    def test_update_comment_owner(self):
        """Comment owner can update their comment."""
        self.client.force_authenticate(user=self.user1)

        update_data = {'content': 'Updated comment'}
        response = self.client.patch(f'/api/v1/comments/{self.comment.id}/', update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment')

    def test_update_comment_non_owner(self):
        """Non-owners cannot update comments."""
        self.client.force_authenticate(user=self.user2)

        update_data = {'content': 'Hacked comment'}
        response = self.client.patch(f'/api/v1/comments/{self.comment.id}/', update_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_owner(self):
        """Comment owner can delete their comment."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(f'/api/v1/comments/{self.comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_non_owner(self):
        """Non-owners cannot delete comments."""
        self.client.force_authenticate(user=self.user2)

        response = self.client.delete(f'/api/v1/comments/{self.comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())


class ReadLaterAPITestCase(TestCase):
    """
    Test ReadLater (bookmarks) API endpoints.

    Tests: List, create, delete.
    Permissions: Users can only see/manage their own bookmarks.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'pass123')
        self.profile1 = Profile.objects.get(user=self.user1)

        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'pass123')
        self.profile2 = Profile.objects.get(user=self.user2)

        # Create writer with articles
        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        writer_profile = Profile.objects.get(user=writer_user)
        writer_profile.role = 'writer'
        writer_profile.save()

        bulletin = Bulletin.objects.create(
            owner=writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )

        self.article1 = Article.objects.create(
            bulletin=bulletin,
            title='Article 1',
            slug='article-1',
            content='Content 1',
            status='published',
            visibility='public'
        )

        self.article2 = Article.objects.create(
            bulletin=bulletin,
            title='Article 2',
            slug='article-2',
            content='Content 2',
            status='published',
            visibility='public'
        )

        # Create bookmark for user1
        self.bookmark = ReadLater.objects.create(
            author=self.profile1,
            article=self.article1
        )

    def test_list_bookmarks_unauthorized(self):
        """Anonymous users cannot list bookmarks."""
        response = self.client.get('/api/v1/bookmarks/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_bookmarks(self):
        """Users can list their own bookmarks."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/bookmarks/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        # Should include article details
        self.assertIn('article_detail', response.data['results'][0])

    def test_list_bookmarks_isolation(self):
        """Users only see their own bookmarks, not others."""
        # Create bookmark for user2
        ReadLater.objects.create(author=self.profile2, article=self.article2)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/bookmarks/')

        # User1 should only see their own bookmark
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['article'], self.article1.id)

    def test_create_bookmark_unauthorized(self):
        """Anonymous users cannot create bookmarks."""
        bookmark_data = {'article': self.article2.id}
        response = self.client.post('/api/v1/bookmarks/', bookmark_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_bookmark(self):
        """Authenticated users can create bookmarks."""
        self.client.force_authenticate(user=self.user1)

        bookmark_data = {'article': self.article2.id}
        response = self.client.post('/api/v1/bookmarks/', bookmark_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ReadLater.objects.filter(
                author=self.profile1,
                article=self.article2
            ).exists()
        )

    def test_delete_bookmark(self):
        """Users can delete their bookmarks."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(f'/api/v1/bookmarks/{self.bookmark.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ReadLater.objects.filter(id=self.bookmark.id).exists())

    def test_retrieve_bookmark(self):
        """Users can retrieve their bookmark details."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(f'/api/v1/bookmarks/{self.bookmark.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['article'], self.article1.id)
        self.assertIn('article_detail', response.data)


class JWTAuthenticationTestCase(TestCase):
    """
    Test JWT authentication endpoints.

    Tests: Obtain token, refresh token, access protected endpoints.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_obtain_token(self):
        """Test obtaining JWT tokens with valid credentials."""
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_invalid_credentials(self):
        """Test token endpoint with invalid credentials."""
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """Test refreshing access token with refresh token."""
        # First, obtain tokens
        token_response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = token_response.data['refresh']

        # Then, refresh
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_access_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with JWT token."""
        # Obtain token
        token_response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        access_token = token_response.data['access']

        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/v1/subscriptions/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token."""
        response = self.client.get('/api/v1/subscriptions/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
