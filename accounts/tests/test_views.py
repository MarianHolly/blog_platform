from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Profile


class SignUpViewTest(TestCase):
    """Test user registration/signup functionality"""

    def setUp(self):
        self.client = Client()

    def test_signup_view_get_returns_form(self):
        """GET request to signup view should display form"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_signup_view_creates_user_with_valid_data(self):
        """POST with valid data should create user and profile"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123'
        })

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

        # User should be created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')

        # Profile should be created with reader role
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.role, 'reader')
        self.assertTrue(profile.is_reader)

    def test_signup_view_creates_profile_with_reader_role(self):
        """New user profile should automatically have reader role"""
        self.client.post(reverse('signup'), {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123'
        })

        user = User.objects.get(username='testuser')
        profile = Profile.objects.get(user=user)

        self.assertEqual(profile.role, 'reader')

    def test_signup_view_rejects_invalid_data(self):
        """POST with invalid data should show form errors"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
            'password1': 'SecurePass123',
            'password2': 'DifferentPass456'
        })

        # Should not redirect
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

        # User should not be created
        self.assertFalse(User.objects.filter(username='newuser').exists())


class LoginViewTest(TestCase):
    """Test user authentication/login functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        Profile.objects.create(user=self.user, role='reader')

    def test_login_view_get_returns_form(self):
        """GET request to login view should display form"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_view_authenticates_user(self):
        """POST with valid credentials should authenticate user"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass123'
        })

        # Should redirect to profile page
        self.assertEqual(response.status_code, 302)
        self.assertIn('profile', response.url)
        self.assertIn('testuser', response.url)

        # User should be in session
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_view_rejects_invalid_password(self):
        """POST with invalid password should not authenticate"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'WrongPassword'
        })

        # Should not redirect
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

        # No user should be in session
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_view_rejects_nonexistent_user(self):
        """POST with nonexistent username should fail"""
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'TestPass123'
        })

        # Should not authenticate
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_view_redirects_authenticated_user(self):
        """Authenticated user accessing login should be redirected"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(reverse('login'))

        # Should redirect (redirect_authenticated_user = True)
        self.assertEqual(response.status_code, 302)


class ProfileDetailViewTest(TestCase):
    """Test user profile display"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        self.profile = Profile.objects.create(user=self.user, role='reader')

    def test_profile_detail_view_get_returns_profile(self):
        """GET profile should display user profile"""
        response = self.client.get(
            reverse('profile', kwargs={'username': 'testuser'})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], self.profile)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_detail_view_shows_user_info(self):
        """Profile page should display user information"""
        response = self.client.get(
            reverse('profile', kwargs={'username': 'testuser'})
        )

        self.assertContains(response, 'testuser')

    def test_profile_detail_view_nonexistent_user_returns_404(self):
        """Accessing nonexistent user profile should return 404"""
        response = self.client.get(
            reverse('profile', kwargs={'username': 'nonexistent'})
        )

        self.assertEqual(response.status_code, 404)

    def test_profile_detail_view_shows_toggle_buttons_for_own_profile(self):
        """Own profile should show toggle buttons"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(
            reverse('profile', kwargs={'username': 'testuser'})
        )

        # Should have flag for showing toggle buttons
        self.assertTrue(response.context.get('show_toggle_buttons'))

    def test_profile_detail_view_hides_toggle_buttons_for_other_profiles(self):
        """Other user's profile should not show toggle buttons"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123'
        )
        Profile.objects.create(user=other_user, role='reader')

        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(
            reverse('profile', kwargs={'username': 'otheruser'})
        )

        # Should not show toggle buttons for other user's profile
        self.assertFalse(response.context.get('show_toggle_buttons'))

    def test_profile_detail_view_hides_toggle_buttons_for_anonymous(self):
        """Anonymous user should not see toggle buttons"""
        response = self.client.get(
            reverse('profile', kwargs={'username': 'testuser'})
        )

        # Anonymous users should not see toggle buttons
        self.assertFalse(response.context.get('show_toggle_buttons'))


class LogoutViewTest(TestCase):
    """Test user logout functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        Profile.objects.create(user=self.user, role='reader')

    def test_logout_clears_session(self):
        """Logout should clear user session"""
        self.client.login(username='testuser', password='TestPass123')
        self.assertIn('_auth_user_id', self.client.session)

        response = self.client.get(reverse('logout'))

        # Session should be cleared
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_redirects_to_home(self):
        """Logout should redirect to home page"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(reverse('logout'))

        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


class PromoteToWriterViewTest(TestCase):
    """Test reader to writer promotion"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='reader',
            email='reader@test.com',
            password='TestPass123'
        )
        self.profile = Profile.objects.create(user=self.user, role='reader')

    def test_promote_to_writer_requires_login(self):
        """Promotion to writer requires user to be logged in"""
        response = self.client.post(
            reverse('promote_to_writer', kwargs={'username': 'reader'})
        )
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_promote_to_writer_changes_role(self):
        """Promoting reader to writer should change role"""
        self.client.login(username='reader', password='TestPass123')
        response = self.client.post(
            reverse('promote_to_writer', kwargs={'username': 'reader'})
        )

        # Role should be updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.role, 'writer')

    def test_promote_to_writer_prevents_other_user_promotion(self):
        """User cannot promote another user to writer"""
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='TestPass123'
        )
        other_profile = Profile.objects.create(user=other_user, role='reader')

        self.client.login(username='reader', password='TestPass123')
        response = self.client.post(
            reverse('promote_to_writer', kwargs={'username': 'other'})
        )

        # Other user's role should not change
        other_profile.refresh_from_db()
        self.assertEqual(other_profile.role, 'reader')

    def test_promote_to_writer_warns_already_writer(self):
        """Attempting to promote already-writer should show warning"""
        self.profile.role = 'writer'
        self.profile.save()

        self.client.login(username='reader', password='TestPass123')
        response = self.client.post(
            reverse('promote_to_writer', kwargs={'username': 'reader'})
        )

        # Role should remain writer
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.role, 'writer')


class PromoteToAdminViewTest(TestCase):
    """Test reader to admin promotion"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='reader',
            email='reader@test.com',
            password='TestPass123'
        )
        self.profile = Profile.objects.create(user=self.user, role='reader')

        # Create superuser
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='AdminPass123'
        )
        Profile.objects.create(user=self.admin, role='admin')

    def test_promote_to_admin_requires_superuser(self):
        """Only superusers can promote to admin"""
        self.client.login(username='reader', password='TestPass123')
        response = self.client.post(
            reverse('promote_to_admin', kwargs={'username': 'reader'})
        )

        # Role should not change
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.role, 'reader')

    def test_promote_to_admin_superuser_can_promote(self):
        """Superuser can promote reader to admin"""
        self.client.login(username='admin', password='AdminPass123')
        response = self.client.post(
            reverse('promote_to_admin', kwargs={'username': 'reader'})
        )

        # Role should change to admin
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.role, 'admin')

    def test_promote_to_admin_prevents_promoting_writer(self):
        """Cannot promote writer to admin"""
        self.profile.role = 'writer'
        self.profile.save()

        self.client.login(username='admin', password='AdminPass123')
        response = self.client.post(
            reverse('promote_to_admin', kwargs={'username': 'reader'})
        )

        # Role should remain writer
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.role, 'writer')

    def test_promote_to_admin_handles_nonexistent_user(self):
        """Promoting nonexistent user should show error"""
        self.client.login(username='admin', password='AdminPass123')
        response = self.client.post(
            reverse('promote_to_admin', kwargs={'username': 'nonexistent'})
        )

        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
