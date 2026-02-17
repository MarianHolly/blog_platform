from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import Profile
from content.models import Article, Bulletin
from engagement.models import Like, ReadLater, Comment


class LikeToggleTestCase(TestCase):
    """
    Test Like toggle functionality and edge cases.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create reader
        self.reader_user = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.reader_profile = Profile.objects.create(user=self.reader_user, role='reader')

        # Create writer and article
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

    def test_like_article_twice_toggles(self):
        """Liking article twice should toggle like on/off."""
        self.client.force_authenticate(user=self.reader_user)

        # First like
        response1 = self.client.post(f'/api/v1/articles/{self.article.slug}/like/')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.data['status'], 'liked')
        self.assertEqual(Like.objects.filter(article=self.article).count(), 1)

        # Second like (toggle off)
        response2 = self.client.post(f'/api/v1/articles/{self.article.slug}/like/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['status'], 'unliked')
        self.assertEqual(Like.objects.filter(article=self.article).count(), 0)

    def test_like_without_authentication(self):
        """Anonymous users cannot like articles."""
        response = self.client.post(f'/api/v1/articles/{self.article.slug}/like/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_nonexistent_article(self):
        """Liking non-existent article should fail."""
        self.client.force_authenticate(user=self.reader_user)

        response = self.client.post('/api/v1/articles/nonexistent-slug/like/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_article_includes_like_status(self):
        """Article detail should include is_liked status for authenticated user."""
        # Create like
        Like.objects.create(author=self.reader_profile, article=self.article)

        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get(f'/api/v1/articles/{self.article.slug}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_liked'])


class BookmarkToggleTestCase(TestCase):
    """
    Test Bookmark toggle functionality and edge cases.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create reader
        self.reader_user = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.reader_profile = Profile.objects.create(user=self.reader_user, role='reader')

        # Create writer and article
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

    def test_bookmark_article_twice_toggles(self):
        """Bookmarking article twice should toggle bookmark on/off."""
        self.client.force_authenticate(user=self.reader_user)

        # First bookmark
        response1 = self.client.post(f'/api/v1/articles/{self.article.slug}/bookmark/')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.data['status'], 'bookmarked')
        self.assertEqual(ReadLater.objects.filter(article=self.article).count(), 1)

        # Second bookmark (toggle off)
        response2 = self.client.post(f'/api/v1/articles/{self.article.slug}/bookmark/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['status'], 'removed')
        self.assertEqual(ReadLater.objects.filter(article=self.article).count(), 0)

    def test_bookmark_without_authentication(self):
        """Anonymous users cannot bookmark articles."""
        response = self.client.post(f'/api/v1/articles/{self.article.slug}/bookmark/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_article_includes_bookmark_status(self):
        """Article detail should include is_bookmarked status for authenticated user."""
        # Create bookmark
        ReadLater.objects.create(author=self.reader_profile, article=self.article)

        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get(f'/api/v1/articles/{self.article.slug}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_bookmarked'])


class DuplicateCommentTestCase(TestCase):
    """
    Test comment uniqueness constraint (one comment per user per article).
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create reader
        self.reader_user = User.objects.create_user('reader', 'reader@test.com', 'pass123')
        self.reader_profile = Profile.objects.create(user=self.reader_user, role='reader')

        # Create writer and article
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

    def test_user_can_only_comment_once_per_article(self):
        """Users should only be able to comment once per article."""
        self.client.force_authenticate(user=self.reader_user)

        # First comment
        response1 = self.client.post('/api/v1/comments/', {
            'article': self.article.id,
            'content': 'First comment'
        })
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Second comment on same article should fail
        response2 = self.client.post('/api/v1/comments/', {
            'article': self.article.id,
            'content': 'Second comment'
        })
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_comment_on_different_articles(self):
        """Users can comment on multiple different articles."""
        # Create second article
        article2 = Article.objects.create(
            bulletin=self.article.bulletin,
            title='Article 2',
            slug='article-2',
            content='Content 2',
            status='published',
            visibility='public'
        )

        self.client.force_authenticate(user=self.reader_user)

        # Comment on first article
        response1 = self.client.post('/api/v1/comments/', {
            'article': self.article.id,
            'content': 'Comment 1'
        })
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Comment on second article should succeed
        response2 = self.client.post('/api/v1/comments/', {
            'article': article2.id,
            'content': 'Comment 2'
        })
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)


class APIResponseFormatTestCase(TestCase):
    """
    Test API response formats match expected structure.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create writer and article
        writer_user = User.objects.create_user('writer', 'writer@test.com', 'pass123')
        self.writer_profile = Profile.objects.create(
            user=writer_user,
            role='writer'
        )

        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Tech Bulletin',
            slug='tech-bulletin',
            description='Tech articles'
        )

        self.article = Article.objects.create(
            bulletin=self.bulletin,
            title='Test Article',
            slug='test-article',
            subtitle='Test subtitle',
            content='<p>Test content</p>',
            status='published',
            visibility='public'
        )

    def test_article_list_response_format(self):
        """Article list should include expected fields."""
        response = self.client.get('/api/v1/articles/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        if response.data['count'] > 0:
            article = response.data['results'][0]
            # Check expected fields
            self.assertIn('id', article)
            self.assertIn('slug', article)
            self.assertIn('title', article)
            self.assertIn('subtitle', article)
            self.assertIn('bulletin', article)
            self.assertIn('author', article)
            self.assertIn('created', article)
            self.assertIn('likes_count', article)
            self.assertIn('comments_count', article)
            # List should NOT include full content
            self.assertNotIn('content', article)

    def test_article_detail_response_format(self):
        """Article detail should include full content and engagement flags."""
        response = self.client.get(f'/api/v1/articles/{self.article.slug}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Detail should include content
        self.assertIn('content', response.data)
        self.assertIn('is_liked', response.data)
        self.assertIn('is_bookmarked', response.data)
        self.assertIn('can_edit', response.data)

    def test_bulletin_response_includes_owner_details(self):
        """Bulletin response should include owner information."""
        response = self.client.get(f'/api/v1/bulletins/{self.bulletin.slug}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('owner', response.data)
        self.assertIn('username', response.data['owner'])
        self.assertIn('full_name', response.data['owner'])

    def test_comment_response_includes_author_name(self):
        """Comment response should include author name."""
        reader_user = User.objects.create_user(
            'reader',
            'reader@test.com',
            'pass123',
            first_name='John',
            last_name='Doe'
        )
        reader_profile = Profile.objects.create(user=reader_user, role='reader')

        comment = Comment.objects.create(
            author=reader_profile,
            article=self.article,
            content='Test comment'
        )

        self.client.force_authenticate(user=reader_user)
        response = self.client.get(f'/api/v1/comments/{comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('author_name', response.data)
        self.assertIn('can_edit', response.data)


class ArticleCountsTestCase(TestCase):
    """
    Test that article includes correct counts for likes/comments.
    """

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create writer and article
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

        # Create readers
        self.reader1_user = User.objects.create_user('reader1', 'r1@test.com', 'pass123')
        self.reader1_profile = Profile.objects.create(user=self.reader1_user, role='reader')

        self.reader2_user = User.objects.create_user('reader2', 'r2@test.com', 'pass123')
        self.reader2_profile = Profile.objects.create(user=self.reader2_user, role='reader')

    def test_likes_count_accuracy(self):
        """Article should show accurate likes count."""
        # Create likes
        Like.objects.create(author=self.reader1_profile, article=self.article)
        Like.objects.create(author=self.reader2_profile, article=self.article)

        response = self.client.get(f'/api/v1/articles/{self.article.slug}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 2)

    def test_comments_count_accuracy(self):
        """Article should show accurate comments count."""
        # Create comments
        Comment.objects.create(
            author=self.reader1_profile,
            article=self.article,
            content='Comment 1'
        )
        Comment.objects.create(
            author=self.reader2_profile,
            article=self.article,
            content='Comment 2'
        )

        response = self.client.get(f'/api/v1/articles/{self.article.slug}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments_count'], 2)

    def test_counts_update_after_deletion(self):
        """Counts should update when likes/comments are deleted."""
        # Create and delete like
        like = Like.objects.create(author=self.reader1_profile, article=self.article)

        response1 = self.client.get(f'/api/v1/articles/{self.article.slug}/')
        self.assertEqual(response1.data['likes_count'], 1)

        like.delete()

        response2 = self.client.get(f'/api/v1/articles/{self.article.slug}/')
        self.assertEqual(response2.data['likes_count'], 0)
