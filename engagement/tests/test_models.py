from django.contrib.auth.models import User
from django.db import IntegrityError
from django.template.defaulttags import comment
from django.test import TestCase
from django.utils import timezone

from accounts.models import Profile
from content.models import Article, Bulletin
from engagement.models import Comment, Like, ReadLater


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nCommentModelTest - setting setUpTestData')

        test_user = User.objects.create_user(
            username='TestUser', password='TestPassword123')
        test_profile = Profile.objects.create(
            user=test_user, role='writer')
        test_bulletin = Bulletin.objects.create(
            owner=test_profile, title='TestBulletin', slug='test-bulletin')
        test_article = Article.objects.create(
            title='TestArticle',
            status='published',
            visibility='public',
            bulletin=test_bulletin,
            published=timezone.now(),
        )

        test_comment = Comment.objects.create(
            author=test_profile, article=test_article, content='Test Comment',
        )

    def test_comment_str(self):
        comment = Comment.objects.get(author__user__username='TestUser')
        expected = f"TestUser commented on TestArticle"
        self.assertEqual(comment.__str__(), expected)

    def test_comment_repr(self):
        comment = Comment.objects.get(author__user__username='TestUser')
        expected = f"Comment(author=TestUser, article=TestArticle)"
        self.assertEqual(comment.__repr__(), expected)

    def test_comment_article(self):
        comment = Comment.objects.get(author__user__username='TestUser')
        self.assertEqual(comment.article.title, 'TestArticle')

    def test_comment_content(self):
        comment = Comment.objects.get(author__user__username='TestUser')
        self.assertEqual(comment.content, 'Test Comment')

    def test_comment_author(self):
        comment = Comment.objects.get(author__user__username='TestUser')
        self.assertEqual(comment.author.user.username, 'TestUser')

    def test_comment_unique_together_constraint(self):
        """Test that duplicate comments (same user+article) raise IntegrityError."""
        comment = Comment.objects.get(author__user__username='TestUser')

        # Attempting to create another comment from same user on same article
        # should raise IntegrityError due to unique_together constraint
        with self.assertRaises(IntegrityError):
            Comment.objects.create(
                author=comment.author,
                article=comment.article,
                content='Duplicate comment'
            )


class LikeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nLikeModelTest - setting setUpTestData')

        test_user = User.objects.create_user(
            username='TestUser', password='TestPassword123')
        test_profile = Profile.objects.create(
            user=test_user, role='writer')
        test_bulletin = Bulletin.objects.create(
            owner=test_profile, title='TestBulletin', slug='test-bulletin')
        test_article = Article.objects.create(
            title='TestArticle',
            status='published',
            visibility='public',
            bulletin=test_bulletin,
            published=timezone.now(),
        )

        test_like = Like.objects.create(
            author=test_profile, article=test_article
        )

    def test_like_repr(self):
        like = Like.objects.get(author__user__username='TestUser')
        expected = f"Like(author=TestUser, article=TestArticle)"
        self.assertEqual(like.__repr__(), expected)

    def test_like_str(self):
        like = Like.objects.get(author__user__username='TestUser')
        expected = f"TestUser liked TestArticle"
        self.assertEqual(like.__str__(), expected)

    def test_like_author(self):
        like = Like.objects.get(author__user__username='TestUser')
        self.assertEqual(like.author.user.username, 'TestUser')

    def test_like_author_relationship(self):
        like = Like.objects.first()
        self.assertEqual(like.author.user.username, 'TestUser')
        self.assertEqual(like.author.role, 'writer')

    def test_like_article(self):
        like = Like.objects.get(author__user__username='TestUser')
        self.assertEqual(like.article.title, 'TestArticle')

    def test_like_own_article(self):
        writer_profile = Profile.objects.get(user__username='TestUser')
        article = Article.objects.get(title='TestArticle')
        like = Like.objects.create(
            author=writer_profile,
            article=article)
        self.assertTrue(Like.objects.filter(author=writer_profile, article=article).exists())

    def test_like_unique_together_constraint(self):
        """Test that duplicate likes (same user+article) raise IntegrityError."""
        like = Like.objects.get(author__user__username='TestUser')

        # Attempting to create another like from same user on same article
        # should raise IntegrityError due to unique_together constraint
        with self.assertRaises(IntegrityError):
            Like.objects.create(
                author=like.author,
                article=like.article
            )



class ReadLaterModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nReadLaterModelTest - setting setUpTestData')

        test_user = User.objects.create_user(
            username='TestUser', password='TestPassword123')
        test_profile = Profile.objects.create(
            user=test_user, role='writer')
        test_bulletin = Bulletin.objects.create(
            owner=test_profile, title='TestBulletin', slug='test-bulletin')
        test_article = Article.objects.create(
            title='TestArticle',
            status='published',
            visibility='public',
            bulletin=test_bulletin,
            published=timezone.now(),
        )

        test_readlater = ReadLater.objects.create(
            author=test_profile, article=test_article
        )

    def test_readlater_repr(self):
        readlater = ReadLater.objects.get(author__user__username='TestUser')
        expected = f"ReadLater(author=TestUser, article=TestArticle)"
        self.assertEqual(readlater.__repr__(), expected)

    def test_readlater_str(self):
        readlater = ReadLater.objects.get(author__user__username='TestUser')
        expected = f"TestUser read later on TestArticle"
        self.assertEqual(readlater.__str__(), expected)

    def test_readlater_author(self):
        readlater = ReadLater.objects.get(author__user__username='TestUser')
        self.assertEqual(readlater.author.user.username, 'TestUser')

    def test_readlater_unique_together_constraint(self):
        """Test that duplicate read-later bookmarks (same user+article) raise IntegrityError."""
        readlater = ReadLater.objects.get(author__user__username='TestUser')

        # Attempting to create another read-later from same user on same article
        # should raise IntegrityError due to unique_together constraint
        with self.assertRaises(IntegrityError):
            ReadLater.objects.create(
                author=readlater.author,
                article=readlater.article
            )