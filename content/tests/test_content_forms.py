from django.contrib.auth.models import User
from django.test import TestCase

from content.models import Article, Bulletin
from accounts.models import Profile


class BulletinFormTest(TestCase):
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

    pass


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