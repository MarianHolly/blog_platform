from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from accounts.models import Profile
from content.models import Bulletin, Article


# Create your tests here.
class BulletinModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('BulletinModel - setting setUpTestData')

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
            slug='bulletin-testing',)

    def test_bulletin_title(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        self.assertEqual(bulletin.title, 'Bulletin Testing')

    def test_bulletin_data(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        self.assertEqual(bulletin.title, 'Bulletin Testing')
        self.assertEqual(bulletin.description, 'Testing of Bulletin')
        self.assertEqual(bulletin.slug, 'bulletin-testing')

    def test_bulletin_owner_role(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        self.assertEqual(bulletin.owner.role, 'writer')

    def test_bulletin_owner_profile(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        self.assertEqual(bulletin.owner.user.username, 'TestUser')
        self.assertEqual(bulletin.owner.user.email, 'test@mail.com')

    def test_bulletin_repr(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        self.assertEqual(bulletin.__repr__(), "Bulletin(title=Bulletin Testing, owner=TestUser)")

    def test_bulletin_str(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        self.assertEqual(bulletin.__str__(), 'Bulletin Testing')

    def test_bulletin_slug_unique(self):
        profile = Profile.objects.get(user__username='TestUser')
        # profile already has bulletin with this slug
        with self.assertRaises(Exception):
            Bulletin.objects.create(
                owner=profile,
                title='Second Bulletin Testing',
                description='Testing of Bulletin',
                slug='bulletin-testing',
            )

    def test_bulletin_title_unique(self):
        profile = Profile.objects.get(user__username='TestUser')
        # profile already has bulletin with this slug
        with self.assertRaises(Exception):
            Bulletin.objects.create(
                owner=profile,
                title='Bulletin Testing',
                description='Testing of Bulletin',
                slug='bulletin-testing-second',
            )


class ArticleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('ArticleModel - setting setUpTestData')

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

    def test_article_data(self):
        article = Article.objects.get(title='Article Testing')
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        self.assertEqual(article.title, 'Article Testing')
        self.assertEqual(article.status, 'published')
        self.assertEqual(article.visibility, 'public')
        self.assertEqual(article.bulletin, bulletin)

    def test_article_title_unique(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        # article with this title already exists in this bulletin
        with self.assertRaises(Exception):
            Article.objects.create(title='Article Testing', status='published', visibility='public', bulletin=bulletin)

    def test_article_writer(self):
        article = Article.objects.get(title='Article Testing')
        self.assertEqual(article.bulletin.owner.user.username, 'TestUser')

    def test_article_author(self):
        article = Article.objects.get(title='Article Testing')
        self.assertEqual(article.author, article.bulletin.owner.user)
        self.assertEqual(article.author.username, 'TestUser')

    def test_article_repr(self):
        article = Article.objects.get(title='Article Testing')
        expected = f"Article(title=Article Testing, created={article.created})"
        self.assertEqual(article.__repr__(), expected)

    def test_article_str(self):
        article = Article.objects.get(title='Article Testing')
        self.assertEqual(article.__str__(), 'Article Testing')

