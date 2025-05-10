from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import Profile


# Create your tests here.
class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nProfileModelTest - setting setUpTestData')

        test_user = User.objects.create_user(
            username='TestUser',
            first_name='Test',
            last_name='User',
            password='TestPassword123',
            email='test@mail.com')

        test_profile = Profile.objects.create(
            user=test_user,
            role='writer'
        )

    def test_profile_repr(self):
        profile = Profile.objects.get(user__username='TestUser')
        expected = f"Profile(name=TestUser, role=writer)"
        self.assertEqual(profile.__repr__(), expected)

    def test_profile_str(self):
        profile = Profile.objects.get(user__username='TestUser')
        self.assertEqual(profile.__str__(), "TestUser")

    def test_profile_role(self):
        profile = Profile.objects.get(user__username='TestUser')
        self.assertEqual(profile.role, 'writer')

    def test_profile_role_property(self):
        profile = Profile.objects.get(user__username='TestUser')
        self.assertTrue(profile.is_writer)

    def test_profile_full_name(self):
        profile = Profile.objects.get(user__username='TestUser')
        self.assertEqual(profile.full_name, "Test User")

    def test_profile_username_unique(self):
        profile1 = Profile.objects.get(user__username='TestUser')
        with self.assertRaises(Exception):
            user2 = User.objects.create_user(
                username='TestUser', password='TestPassword234')
            Profile.objects.create(
                user=user2, role='writer')


class SignUpFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nSignUpFormTest - setting setUpTestData')

    pass


class ProfileFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nProfileFormTest - setting setUpTestData')

    pass