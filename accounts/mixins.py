from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


class ReaderRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Musíte byť prihlásený.')
            return redirect('login')
        raise PermissionDenied('Musíte byť prihlásený.')


class WriterRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        try:
            return user.profile.is_writer
        except:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Musíte byť prihlásený.')
            return redirect('login')
        # Return 403 for authenticated users without permission
        raise PermissionDenied('Potrebujete autorské oprávnenia.')


class WriterOrSuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False

        # Allow superusers
        if user.is_superuser:
            return True

        # Allow writers
        try:
            return user.profile.is_writer
        except:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Musíte byť prihlásený.')
            return redirect('login')
        raise PermissionDenied('Potrebujete autorské alebo administrátorské oprávnenia.')


class AdministratorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        try:
            return user.profile.is_admin
        except:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Musíte byť prihlásený.')
            return redirect('login')
        raise PermissionDenied('Potrebujete administrátorské oprávnenia.')