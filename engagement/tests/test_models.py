from django.contrib.auth.models import User
from django.template.defaulttags import comment
from django.test import TestCase
from django.utils import timezone

from accounts.models import Profile
from content.models import Article, Bulletin
from engagement.models import Comment


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


class LikeModelTest(TestCase):
    pass


class ReadLaterModelTest(TestCase):
    pass