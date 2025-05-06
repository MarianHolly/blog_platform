from django.contrib.auth.models import User
from django.test import TestCase

from content.forms import ArticleForm, BulletinForm
from content.models import Article, Bulletin
from accounts.models import Profile


class BulletinFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('setUpTestData for BulletinForm')

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
                  'description': 'Testing of Bulletin'}
        )
        self.assertTrue(form.is_valid())

    def test_bulletin_form_is_valid_without_description(self):
        form = BulletinForm(
            data={'title': 'Bulletin Testing',
                  'slug': 'bulletin-testing'}
        )
        self.assertTrue(form.is_valid())

    def test_bulletin_form_is_not_valid_without_title(self):
        form = BulletinForm(
            data={'title': '', 'slug': 'bulletin-testing'}
        )
        self.assertFalse(form.is_valid())

    def test_bulletin_form_is_not_valid_without_slug(self):
        form = BulletinForm(
            data={'title': 'Bulletin Testing', 'slug': ''}
        )
        self.assertFalse(form.is_valid())


class ArticleFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
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

    pass