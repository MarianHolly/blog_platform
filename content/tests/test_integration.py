from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from content.models import Article, Bulletin, Subscription
from engagement.models import Like, Comment, ReadLater


class ReaderSignupAndDiscoverWorkflowTest(TestCase):
    """Test complete reader workflow: signup → discover articles → engage"""

    def setUp(self):
        self.client = Client()

        # Create writer with published article
        self.writer = User.objects.create_user(
            username='writer',
            email='writer@test.com',
            password='pass123'
        )
        self.writer_profile = Profile.objects.create(user=self.writer, role='writer')
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Tech News',
            slug='tech-news'
        )
        self.article = Article.objects.create(
            title='Django Best Practices',
            content='<p>Learn Django best practices</p>',
            bulletin=self.bulletin,
            status='published',
            visibility='public',
            published=timezone.now()
        )

    def test_reader_signup_discover_and_like_workflow(self):
        """Test reader can signup, find article, and like it"""
        # Step 1: Reader signs up
        signup_response = self.client.post(reverse('signup'), {
            'username': 'newreader',
            'first_name': 'New',
            'last_name': 'Reader',
            'email': 'reader@example.com',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123'
        })
        self.assertEqual(signup_response.status_code, 302)

        # Verify user and profile created
        self.assertTrue(User.objects.filter(username='newreader').exists())
        reader_user = User.objects.get(username='newreader')
        reader_profile = Profile.objects.get(user=reader_user)
        self.assertTrue(reader_profile.is_reader)

        # Step 2: Reader logs in
        login_result = self.client.login(username='newreader', password='SecurePass123')
        self.assertTrue(login_result)

        # Step 3: Reader discovers and views article
        article_response = self.client.get(
            reverse('article_detail', args=[self.article.id])
        )
        self.assertEqual(article_response.status_code, 200)
        self.assertContains(article_response, 'Django Best Practices')

        # Step 4: Reader likes the article
        like_response = self.client.post(
            reverse('toggle_like', args=[self.article.id]),
            {'next': reverse('article_detail', args=[self.article.id])}
        )
        self.assertEqual(like_response.status_code, 302)

        # Verify like was created
        self.assertTrue(Like.objects.filter(
            article=self.article,
            author=reader_profile
        ).exists())

    def test_reader_signup_discover_and_comment_workflow(self):
        """Test reader can signup, find article, and comment on it"""
        # Step 1: Reader signs up
        self.client.post(reverse('signup'), {
            'username': 'commenter',
            'first_name': 'Comment',
            'last_name': 'Maker',
            'email': 'commenter@example.com',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123'
        })

        # Step 2: Reader logs in
        self.client.login(username='commenter', password='SecurePass123')
        reader_user = User.objects.get(username='commenter')
        reader_profile = Profile.objects.get(user=reader_user)

        # Step 3: Reader views article
        article_response = self.client.get(
            reverse('article_detail', args=[self.article.id])
        )
        self.assertEqual(article_response.status_code, 200)

        # Step 4: Reader comments on article
        comment_response = self.client.post(
            reverse('article_detail', args=[self.article.id]),
            {'content': 'Great article about Django!'}
        )

        # Verify comment was created
        self.assertTrue(Comment.objects.filter(
            article=self.article,
            author=reader_profile
        ).exists())
        comment = Comment.objects.get(article=self.article, author=reader_profile)
        self.assertEqual(comment.content, 'Great article about Django!')


class WriterCreateAndPublishWorkflowTest(TestCase):
    """Test complete writer workflow: create → publish → article appears in bulletin"""

    def setUp(self):
        self.client = Client()

        # Create writer
        self.writer = User.objects.create_user(
            username='writer',
            email='writer@test.com',
            password='pass123'
        )
        self.writer_profile = Profile.objects.create(user=self.writer, role='writer')
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='My Bulletin',
            slug='my-bulletin'
        )

    def test_writer_create_and_publish_article_workflow(self):
        """Test writer can create article as draft and publish it"""
        # Step 1: Writer logs in
        login_result = self.client.login(username='writer', password='pass123')
        self.assertTrue(login_result)

        # Step 2: Writer creates article
        self.client.post(reverse('article_create'), {
            'title': 'New Article',
            'content': '<p>Article content</p>',
            'status': 'draft',
            'visibility': 'private'
        })

        # Verify article created as draft
        self.assertTrue(Article.objects.filter(title='New Article').exists())
        article = Article.objects.get(title='New Article')
        self.assertEqual(article.status, 'draft')
        self.assertEqual(article.visibility, 'private')

        # Step 3: Writer publishes article
        article.status = 'published'
        article.visibility = 'public'
        article.save()

        # Verify article is now published and public
        article.refresh_from_db()
        self.assertEqual(article.status, 'published')
        self.assertEqual(article.visibility, 'public')
        self.assertIsNotNone(article.published)

        # Step 4: Verify article appears in bulletin
        bulletin_response = self.client.get(
            reverse('bulletin_detail', args=[self.bulletin.slug])
        )
        self.assertContains(bulletin_response, 'New Article')


class ReaderSubscribeAndViewPrivateArticlesTest(TestCase):
    """Test reader can subscribe to bulletin and view private articles"""

    def setUp(self):
        self.client = Client()

        # Create writer with private article
        self.writer = User.objects.create_user(
            username='writer',
            email='writer@test.com',
            password='pass123'
        )
        self.writer_profile = Profile.objects.create(user=self.writer, role='writer')
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Premium Content',
            slug='premium-content'
        )
        self.private_article = Article.objects.create(
            title='Premium Article',
            content='<p>Only for subscribers</p>',
            bulletin=self.bulletin,
            status='published',
            visibility='private',
            published=timezone.now()
        )

        # Create reader
        self.reader = User.objects.create_user(
            username='reader',
            email='reader@test.com',
            password='pass123'
        )
        self.reader_profile = Profile.objects.create(user=self.reader, role='reader')

    def test_reader_subscribe_to_bulletin_workflow(self):
        """Test reader can subscribe to bulletin and view private articles"""
        # Step 1: Reader logs in
        login_result = self.client.login(username='reader', password='pass123')
        self.assertTrue(login_result)

        # Step 2: Reader subscribes to bulletin
        subscription = Subscription.objects.create(
            subscriber=self.reader_profile,
            bulletin=self.bulletin
        )
        self.assertTrue(Subscription.objects.filter(
            subscriber=self.reader_profile,
            bulletin=self.bulletin
        ).exists())

        # Step 3: Reader accesses bulletin
        bulletin_response = self.client.get(
            reverse('bulletin_detail', args=[self.bulletin.slug])
        )
        self.assertEqual(bulletin_response.status_code, 200)

        # Step 4: Reader can view article (they're subscribed)
        article_response = self.client.get(
            reverse('article_detail', args=[self.private_article.id])
        )
        self.assertEqual(article_response.status_code, 200)
        self.assertContains(article_response, 'Premium Article')


class MultiUserEngagementWorkflowTest(TestCase):
    """Test multiple users engaging with same article"""

    def setUp(self):
        self.client = Client()

        # Create writer and article
        self.writer = User.objects.create_user(
            username='writer',
            email='writer@test.com',
            password='pass123'
        )
        self.writer_profile = Profile.objects.create(user=self.writer, role='writer')
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Popular Article',
            slug='popular-article'
        )
        self.article = Article.objects.create(
            title='Popular Post',
            content='<p>Everyone wants to engage</p>',
            bulletin=self.bulletin,
            status='published',
            visibility='public',
            published=timezone.now()
        )

        # Create multiple readers
        self.reader1 = User.objects.create_user(
            username='reader1',
            email='reader1@test.com',
            password='pass123'
        )
        self.reader1_profile = Profile.objects.create(user=self.reader1, role='reader')

        self.reader2 = User.objects.create_user(
            username='reader2',
            email='reader2@test.com',
            password='pass123'
        )
        self.reader2_profile = Profile.objects.create(user=self.reader2, role='reader')

    def test_multiple_readers_engage_with_article(self):
        """Test multiple readers can like and comment on same article"""
        # Reader 1 logs in and likes
        self.client.login(username='reader1', password='pass123')
        self.client.post(
            reverse('toggle_like', args=[self.article.id]),
            {'next': '/'}
        )
        self.client.logout()

        # Verify reader1's like
        self.assertTrue(Like.objects.filter(
            article=self.article,
            author=self.reader1_profile
        ).exists())

        # Reader 2 logs in and likes
        self.client.login(username='reader2', password='pass123')
        self.client.post(
            reverse('toggle_like', args=[self.article.id]),
            {'next': '/'}
        )
        self.client.logout()

        # Verify reader2's like
        self.assertTrue(Like.objects.filter(
            article=self.article,
            author=self.reader2_profile
        ).exists())

        # Verify article has 2 likes total
        self.assertEqual(Like.objects.filter(article=self.article).count(), 2)

    def test_multiple_readers_comment_on_article(self):
        """Test multiple readers can comment on same article"""
        # Reader 1 logs in and comments
        self.client.login(username='reader1', password='pass123')
        self.client.post(
            reverse('article_detail', args=[self.article.id]),
            {'content': 'Reader 1 comment'}
        )
        self.client.logout()

        # Reader 2 logs in and comments
        self.client.login(username='reader2', password='pass123')
        self.client.post(
            reverse('article_detail', args=[self.article.id]),
            {'content': 'Reader 2 comment'}
        )
        self.client.logout()

        # Verify both comments exist
        self.assertTrue(Comment.objects.filter(
            article=self.article,
            author=self.reader1_profile
        ).exists())
        self.assertTrue(Comment.objects.filter(
            article=self.article,
            author=self.reader2_profile
        ).exists())

        # Verify correct comment text
        comment1 = Comment.objects.get(article=self.article, author=self.reader1_profile)
        comment2 = Comment.objects.get(article=self.article, author=self.reader2_profile)
        self.assertEqual(comment1.content, 'Reader 1 comment')
        self.assertEqual(comment2.content, 'Reader 2 comment')

    def test_reader_update_comment(self):
        """Test reader can update their comment"""
        # Create initial comment
        Comment.objects.create(
            article=self.article,
            author=self.reader1_profile,
            content='Initial comment'
        )

        # Reader logs in and updates comment
        self.client.login(username='reader1', password='pass123')
        self.client.post(
            reverse('article_detail', args=[self.article.id]),
            {'content': 'Updated comment'}
        )

        # Verify comment is updated, not duplicated
        comments = Comment.objects.filter(
            article=self.article,
            author=self.reader1_profile
        )
        self.assertEqual(comments.count(), 1)
        self.assertEqual(comments.first().content, 'Updated comment')
