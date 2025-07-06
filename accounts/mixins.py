from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

class ReaderRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        messages.error(self.request, 'Musíte byť prihlásený.')
        return redirect('login')


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
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Potrebujete autorské oprávnenia.')
            return redirect('profile', username=self.request.user.username)
        return redirect('login')


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
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Potrebujete administrátorské oprávnenia.')
            return redirect('profile', username=self.request.user.username)
        return redirect('login')