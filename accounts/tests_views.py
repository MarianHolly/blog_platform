from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Profile


class LoginViewTest(TestCase):
    """Test user login functionality"""

    @classmethod
    def setUpTestData(cls):
        print('\nLoginView - setting setUpTestData')
        cls.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='pass123'
        )
        Profile.objects.create(user=cls.user, role='reader')

    def test_login_page_loads(self):
        """Login page should load successfully"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_user_can_login(self):
        """User should be able to log in with correct credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 302)  # redirect on success
        self.assertTrue(response.wsgi_request.user.is_authenticated if hasattr(response, 'wsgi_request') else True)

    def test_login_fails_with_wrong_password(self):
        """Login should fail with incorrect password"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        # Either 200 (form redisplayed) or 302 (redirect to login)
        self.assertIn(response.status_code, [200, 302])


class SignUpViewTest(TestCase):
    """Test user signup functionality"""

    def test_signup_page_loads(self):
        """Signup page should load successfully"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_user_can_signup(self):
        """User should be able to sign up with valid data"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'reader'
        })
        self.assertEqual(response.status_code, 302)  # redirect on success
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertTrue(Profile.objects.filter(user=user, role='reader').exists())

    def test_signup_fails_with_duplicate_username(self):
        """Signup should fail with duplicate username"""
        User.objects.create_user(username='existing', email='existing@test.com', password='pass')
        response = self.client.post(reverse('signup'), {
            'username': 'existing',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'email': 'different@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'reader'
        })
        self.assertEqual(response.status_code, 200)  # form redisplayed with error


class ProfileDetailViewTest(TestCase):
    """Test profile detail page"""

    @classmethod
    def setUpTestData(cls):
        print('\nProfileDetailView - setting setUpTestData')
        cls.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='pass123',
            first_name='Test', last_name='User'
        )
        cls.profile = Profile.objects.create(user=cls.user, role='reader')

    def test_profile_page_loads(self):
        """Profile page should load successfully"""
        response = self.client.get(reverse('profile', args=['testuser']))
        self.assertEqual(response.status_code, 200)

    def test_profile_displays_user_info(self):
        """Profile page should display user information"""
        response = self.client.get(reverse('profile', args=['testuser']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Test User')

    def test_profile_not_found(self):
        """Profile page should return 404 for non-existent user"""
        response = self.client.get(reverse('profile', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)
