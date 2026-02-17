import time
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from accounts.models import Profile
from content.models import Bulletin, Article, Subscription


class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nProfileModel - setting setUpTestData')

        # Create test reader
        cls.reader_user = User.objects.create_user(
            username='TestReader',
            password='TestPassword123',
            email='reader@mail.com')
        cls.reader_profile = cls.reader_user.profile  # Use auto-created profile

        cls.reader_profile.role = 'reader'

        cls.reader_profile.save()

        # Create test writer
        cls.writer_user = User.objects.create_user(
            username='TestWriter',
            password='TestPassword456',
            email='writer@mail.com')
        cls.writer_profile = cls.writer_user.profile  # Use auto-created profile

        cls.writer_profile.role = 'writer'

        cls.writer_profile.save()

        # Create test admin
        cls.admin_user = User.objects.create_user(
            username='TestAdmin',
            password='TestPassword789',
            email='admin@mail.com')
        cls.admin_profile = cls.admin_user.profile  # Use auto-created profile

        cls.admin_profile.role = 'admin'

        cls.admin_profile.save()

    def test_reader_profile_is_reader_returns_true(self):
        """Reader profile should have is_reader property return True"""
        profile = Profile.objects.get(user__username='TestReader')
        self.assertTrue(profile.is_reader)

    def test_reader_profile_is_writer_returns_false(self):
        """Reader profile should have is_writer property return False"""
        profile = Profile.objects.get(user__username='TestReader')
        self.assertFalse(profile.is_writer)

    def test_reader_profile_is_admin_returns_false(self):
        """Reader profile should have is_admin property return False"""
        profile = Profile.objects.get(user__username='TestReader')
        self.assertFalse(profile.is_admin)

    def test_writer_profile_is_writer_returns_true(self):
        """Writer profile should have is_writer property return True"""
        profile = Profile.objects.get(user__username='TestWriter')
        self.assertTrue(profile.is_writer)

    def test_writer_profile_has_bulletin(self):
        """Writer profile should have an associated bulletin"""
        profile = Profile.objects.get(user__username='TestWriter')
        # Create a bulletin for the writer
        bulletin = Bulletin.objects.create(
            owner=profile,
            title='Test Bulletin',
            slug='test-bulletin')
        # Verify bulletin exists and is associated with writer
        self.assertTrue(Bulletin.objects.filter(owner=profile).exists())
        self.assertEqual(bulletin.owner, profile)

    def test_admin_profile_is_admin_returns_true(self):
        """Admin profile should have is_admin property return True"""
        profile = Profile.objects.get(user__username='TestAdmin')
        self.assertTrue(profile.is_admin)


# Create your tests here.
class BulletinModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nBulletinModel - setting setUpTestData')

        test_user = User.objects.create_user(
            username='TestUser',
            password='TestPassword123',
            email='test@mail.com')

        test_profile = test_user.profile  # Use auto-created profile


        test_profile.role = 'writer'


        test_profile.save()

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
        print('\nArticleModel - setting setUpTestData')

        test_user = User.objects.create_user(
            username='TestUser',
            password='TestPassword123',
            email='test@mail.com')

        test_profile = test_user.profile  # Use auto-created profile


        test_profile.role = 'writer'


        test_profile.save()

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
        self.assertEqual(article.author.user, article.bulletin.owner.user)
        self.assertEqual(article.author.user.username, 'TestUser')

    def test_article_repr(self):
        article = Article.objects.get(title='Article Testing')
        expected = f"Article(title=Article Testing, status={article.status}, evaluation={article.evaluation})"
        self.assertEqual(article.__repr__(), expected)

    def test_article_str(self):
        article = Article.objects.get(title='Article Testing')
        self.assertEqual(article.__str__(), 'Article Testing')

    def test_article_published_date_status_set(self):
        # testing is publishing date is set if draft is changed to published
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        article = Article.objects.create(
            title='Publishing Test Article',
            status='draft',
            visibility='private',
            bulletin=bulletin)
        # article is without published date
        self.assertIsNone(article.published)
        article.status = 'published'
        article.save()
        # article has published date
        self.assertIsNotNone(article.published)

    def test_article_published_date_status_change(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        article = Article.objects.create(
            title='Republishing Test Article',
            status='published',
            visibility='private',
            bulletin=bulletin
        )
        first_date = article.published
        # change status to 'draft'
        article.status = 'draft'
        article.save()
        # time between change back to 'published'
        time.sleep(1)
        # change status to 'published'
        article.status = 'published'
        article.save()
        # check if published date is changed
        self.assertNotEqual(first_date, article.published)


class SubscriptionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nSubscriptionModel - setting setUpTestData')

        writer_user = User.objects.create_user(
            username='TestWriter', password='TestPassword123')
        writer_profile = writer_user.profile  # Use auto-created profile

        writer_profile.role = 'writer'

        writer_profile.save()
        writer_bulletin = Bulletin.objects.create(
            owner=writer_profile, title='Subscription Testing', slug='subscription-testing')

        reader_user = User.objects.create_user(
            username='TestReader', password='TestPassword456')
        reader_profile = reader_user.profile  # Use auto-created profile

        reader_profile.role = 'reader'

        reader_profile.save()

        subscription = Subscription.objects.create(
            subscriber=reader_profile, bulletin=writer_bulletin)

    def test_subscription_srt(self):
        subscription = Subscription.objects.get(bulletin__slug='subscription-testing')
        expected = f"TestReader subscribed to 'Subscription Testing'"
        self.assertEqual(subscription.__str__(), expected)

    def test_subscription_repr(self):
        subscription = Subscription.objects.get(bulletin__slug='subscription-testing')
        expected = f"Subscription(subscriber=TestReader, bulletin=Subscription Testing)"
        self.assertEqual(subscription.__repr__(), expected)

    def test_subscription_data(self):
        subscription = Subscription.objects.get(bulletin__slug='subscription-testing')
        self.assertEqual(subscription.bulletin.title, 'Subscription Testing')
        self.assertEqual(subscription.subscriber.user.username, 'TestReader')

    def test_subscription_unique(self):
        reader = Profile.objects.get(user__username='TestReader')
        bulletin = Bulletin.objects.get(title='Subscription Testing')
        with self.assertRaises(Exception):
            Subscription.objects.create(
                subscriber=reader, bulletin=bulletin)