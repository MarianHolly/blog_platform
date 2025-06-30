from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from django.test import TestCase, Client

from accounts.models import Profile
from accounts.forms import SignUpForm
from content.models import Bulletin, Article


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
        with self.assertRaises(IntegrityError):
            user2 = User.objects.create_user(
                username='TestUser', password='TestPassword234')


class SignUpFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nSignUpFormTest - setting setUpTestData')

        test_user = User.objects.create_user(
            username='TestUser', password='TestPassword123')
        test_profile = Profile.objects.create(
            user=test_user, role='reader')

    def test_signup_form_valid(self):
        form = SignUpForm(
            data = {
                'username': 'TestUser2',
                'password1': 'TestPassword123',
                'password2': 'TestPassword123',
                'email': 'test@mail.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'reader'
            }
        )
        self.assertTrue(form.is_valid())

    def test_signup_form_username_taken(self):
        form = SignUpForm(
            data={
                'username': 'TestUser',
                'password1': 'TestPassword123',
                'password2': 'TestPassword123',
                'email': 'test@mail.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'administrator'
            }
        )
        self.assertFalse(form.is_valid())


    def test_signup_form_without_email(self):
        form = SignUpForm(
            data={
                'username': 'TestUser',
                'password1': 'TestPassword123',
                'password2': 'TestPassword123',
                'email': '',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'reader'
            }
        )
        self.assertFalse(form.is_valid())

    def test_signup_form_invalid_email(self):
        form = SignUpForm(
            data={
                'username': 'TestUser',
                'password1': 'TestPassword123',
                'password2': 'TestPassword123',
                'email': 'testmail.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'reader'
            }
        )
        self.assertFalse(form.is_valid())

    def test_signup_form_without_password1(self):
        form = SignUpForm(
            data={
                'username': 'TestUser',
                'password1': '',
                'password2': 'TestPassword123',
                'email': 'testmail.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'reader'
            }
        )
        self.assertFalse(form.is_valid())

    def test_signup_form_without_password2(self):
        form = SignUpForm(
            data={
                'username': 'TestUser',
                'password1': 'TestPassword123',
                'password2': '',
                'email': 'testmail.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'reader'
            }
        )
        self.assertFalse(form.is_valid())

    def test_signup_form_passwords_not_match(self):
        form = SignUpForm(
            data={
                'username': 'TestUser',
                'password1': 'TestPassword123',
                'password2': 'TestPassword1234',
                'email': 'testmail.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'reader'
            }
        )
        self.assertFalse(form.is_valid())


class CriticalSecurityTests(TestCase):
    def setUp(self):
        # create Reader
        self.reader_user = User.objects.create_user('reader', 'rsecurity@test.com', 'Security123')
        Profile.objects.create(user=self.reader_user, role='reader')

        # create Writer
        self.writer_user = User.objects.create_user('writer', 'wsecurity@test.com', 'Security234')
        Profile.objects.create(user=self.writer_user, role='writer')

    def test_reader_cannot_create_article(self):
        """CRITICAL: Verify readers can't create articles"""
        self.client.login(username='reader', password='Security123')
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 403, "SECURITY BREACH: Reader can create articles!")

    def test_unauthenticated_cannot_create_article(self):
        """CRITICAL: Verify anonymous users can't create articles"""
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 302, "SECURITY BREACH: Anonymous user can create articles!")


class PermissionTests(TestCase):
    """Test role-based permissions"""

    def setUp(self):
        # Create users with different roles
        self.reader_user = User.objects.create_user('reader', 'reader@test.com', 'Password123')
        self.reader_profile = Profile.objects.create(user=self.reader_user, role='reader')

        self.writer_user = User.objects.create_user('writer', 'writer@test.com', 'Password123')
        self.writer_profile = Profile.objects.create(user=self.writer_user, role='writer')

        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'Password123')
        self.admin_profile = Profile.objects.create(user=self.admin_user, role='admin')

        # Create bulletin and article
        self.bulletin = Bulletin.objects.create(
            owner=self.writer_profile,
            title='Test Bulletin',
            slug='test-bulletin'
        )
        self.article = Article.objects.create(
            title='Test Article',
            bulletin=self.bulletin,
            status='published',
            visibility='public'
        )

    def test_reader_cannot_create_article(self):
        """Readers should not be able to create articles"""
        self.client.login(username='reader', password='Password123')
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_writer_can_create_article(self):
        """Writers should be able to create articles"""
        self.client.login(username='writer', password='Password123')
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 200)