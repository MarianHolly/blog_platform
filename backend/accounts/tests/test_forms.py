from django.contrib.auth.models import User
from django.test import TestCase

from accounts.forms import SignUpForm
from accounts.models import Profile


class SignUpFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nSignUpFormTest - setting setUpTestData')

    def test_signup_form_requires_username(self):
        """Test that username field is required"""
        form = SignUpForm(
            data={
                'username': '',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'password1': 'SecurePass123',
                'password2': 'SecurePass123'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_signup_form_requires_email(self):
        """Test that email field is required"""
        form = SignUpForm(
            data={
                'username': 'johndoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': '',
                'password1': 'SecurePass123',
                'password2': 'SecurePass123'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_signup_form_requires_password(self):
        """Test that password field is required"""
        form = SignUpForm(
            data={
                'username': 'johndoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'password1': '',
                'password2': 'SecurePass123'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_signup_form_password_confirmation_matches(self):
        """Test that password confirmation must match password"""
        form = SignUpForm(
            data={
                'username': 'johndoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'password1': 'SecurePass123',
                'password2': 'DifferentPass456'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_signup_form_creates_user_and_profile(self):
        """Test that form creates both User and Profile with reader role"""
        form = SignUpForm(
            data={
                'username': 'johndoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'password1': 'SecurePass123',
                'password2': 'SecurePass123'
            }
        )
        self.assertTrue(form.is_valid())

        user = form.save()

        # Verify user was created
        self.assertTrue(User.objects.filter(username='johndoe').exists())
        self.assertEqual(user.username, 'johndoe')
        self.assertEqual(user.email, 'john@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

        # Verify profile was created with reader role
        profile = Profile.objects.get(user=user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.role, 'reader')
        self.assertTrue(profile.is_reader)

    def test_signup_form_rejects_duplicate_username(self):
        """Test that duplicate usernames are rejected"""
        # Create first user
        User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='SecurePass123'
        )

        # Try to create second user with same username
        form = SignUpForm(
            data={
                'username': 'johndoe',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': 'jane@example.com',
                'password1': 'SecurePass123',
                'password2': 'SecurePass123'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_signup_form_rejects_duplicate_email(self):
        """Test that duplicate emails are rejected"""
        # Create first user
        User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='SecurePass123'
        )

        # Try to create second user with same email
        form = SignUpForm(
            data={
                'username': 'janedoe',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'password1': 'SecurePass123',
                'password2': 'SecurePass123'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_signup_form_rejects_invalid_username_characters(self):
        """Test that username with invalid characters is rejected"""
        form = SignUpForm(
            data={
                'username': 'john-doe!',  # Invalid characters
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'password1': 'SecurePass123',
                'password2': 'SecurePass123'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_signup_form_accepts_valid_data(self):
        """Test that form accepts valid data"""
        form = SignUpForm(
            data={
                'username': 'johndoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'password1': 'SecurePass123',
                'password2': 'SecurePass123'
            }
        )
        self.assertTrue(form.is_valid())
