from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import Profile
from content.models import Bulletin


# Create your tests here.

class BulletinModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('setUpTestData')

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
        # print(repr(bulletin))
        self.assertEqual(bulletin.__repr__(), "Bulletin(title=Bulletin Testing, owner=TestUser)")

    def test_bulletin_str(self):
        bulletin = Bulletin.objects.get(slug='bulletin-testing')
        self.assertEqual(bulletin.__str__(), 'Bulletin Testing')
