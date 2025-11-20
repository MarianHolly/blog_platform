from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from content.forms import ArticleForm, BulletinForm
from content.models import Article, Bulletin
from accounts.models import Profile


class BulletinFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nBulletinFormTest - setting setUpTestData')

        test_user = User.objects.create_user(
            username='TestUser',
            password='TestPassword123',
            email='test@mail.com')

        test_profile = Profile.objects.create(
            user=test_user,
            role='writer')

    def test_bulletin_form_is_valid(self):
        form = BulletinForm(
            data={'title': 'Bulletin Testing',
                  'slug': 'bulletin-testing',
                  'description': 'Testing of Bulletin'})
        self.assertTrue(form.is_valid())

    def test_bulletin_form_without_title(self):
        form = BulletinForm(
            data={'title': '  ', 'slug': 'bulletin-testing'})
        self.assertFalse(form.is_valid())

    def test_bulletin_form_without_slug(self):
        form = BulletinForm(
            data={'title': 'Bulletin Testing', 'slug': '   '})
        self.assertFalse(form.is_valid())

    def test_bulletin_form_without_description(self):
        form = BulletinForm(
            data={'title': 'Bulletin Testing',
                  'slug': 'bulletin-testing'})
        self.assertTrue(form.is_valid())


class ArticleFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nArticleFormTest - setting setUpTestData')

        test_user = User.objects.create_user(
            username='TestUser',
            password='TestPassword123',
            email='test@mail.com')

        test_profile = Profile.objects.create(
            user=test_user,
            role='writer')

        test_bulletin = Bulletin.objects.create(
            owner=test_profile,
            title='Bulletin Testing',
            description='Testing of Bulletin',
            slug='bulletin-testing', )

        test_article = Article.objects.create(
            title='Article Testing',
            status='published',
            visibility='public',
            bulletin=test_bulletin,
            published=timezone.now(),
        )

    def test_article_form_is_valid(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        form = ArticleForm(
            data={'title': 'Testing of Article',
                  'status': 'draft',
                  'visibility': 'private',
                  'content': 'Content for testing',
                  'bulletin': bulletin}
        )
        self.assertTrue(form.is_valid())

    def test_article_form_title_empty(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        form = ArticleForm(
            data={'title': '       ',
                  'status': 'draft',
                  'visibility': 'private',
                  'bulletin': bulletin}
        )
        self.assertFalse(form.is_valid())

    def test_article_form_status_empty(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        form = ArticleForm(
            data={'title': 'Second Testing',
                  'status': '       ',
                  'visibility': 'private',
                  'bulletin': bulletin}
        )
        self.assertFalse(form.is_valid())

    def test_article_form_status_option(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        form = ArticleForm(
            data={'title': 'Second Testing',
                  'status': 'unpublished',
                  'visibility': 'private',
                  'bulletin': bulletin}
        )
        self.assertFalse(form.is_valid())

    def test_article_form_visibility_empty(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        form = ArticleForm(
            data={'title': 'Third Testin',
                  'status': 'draft',
                  'visibility': '       ',
                  'bulletin': bulletin}
        )
        self.assertFalse(form.is_valid())

    def test_article_form_visibility_option(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        form = ArticleForm(
            data={'title': 'Third Testin',
                  'status': 'draft',
                  'visibility': 'hidden',
                  'bulletin': bulletin}
        )
        self.assertFalse(form.is_valid())

    def test_article_form_bulletin_set_from_user(self):
        user = User.objects.get(username='TestUser')
        form_data = {
            'title': 'New Article From Test',
            'status': 'draft',
            'visibility': 'private',
            'content': 'Content for testing',
        }
        form = ArticleForm(data=form_data, user=user)
        self.assertTrue(form.is_valid())

    def test_article_form_content_required(self):
        """Test that content field is required (mandatory)"""
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        form = ArticleForm(
            data={
                'title': 'Article Without Content',
                'status': 'draft',
                'visibility': 'private',
                'bulletin': bulletin,
                'content': ''  # Empty content
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_article_form_content_cannot_be_only_whitespace(self):
        """Test that content with only HTML tags is invalid"""
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        form = ArticleForm(
            data={
                'title': 'Article With Empty HTML',
                'status': 'draft',
                'visibility': 'private',
                'bulletin': bulletin,
                'content': '<p>&nbsp;</p>'  # Only whitespace in HTML
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_article_form_content_valid_with_text(self):
        """Test that content with actual text is valid"""
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        form = ArticleForm(
            data={
                'title': 'Article With Valid Content',
                'status': 'draft',
                'visibility': 'private',
                'bulletin': bulletin,
                'content': '<p>This is actual content with text.</p>'
            }
        )
        self.assertTrue(form.is_valid())
