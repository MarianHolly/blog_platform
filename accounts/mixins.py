from django.contrib.auth.mixins import UserPassesTestMixin


class ReaderRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated


class WriterRequiredMixin(UserPassesTestMixin):
    """ Writer Role required """
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.profile.role == 'writer'


class BasicAdminRequiredMixin(UserPassesTestMixin):
    """ Basic Admin Role required """
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.profile.role == 'admin'


class SuperAdminRequiredMixin(UserPassesTestMixin):
    """ Only SuperAdmin """
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.profile.is_super_admin

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Iba Super Administrátor má prístup k tejto funkcii.')
            return redirect('profile', username=self.request.user.username)
        return super().handle_no_permission()


class AdminRequiredMixin(UserPassesTestMixin):
    """Either Basic Admin or Super Admin"""
    def test_func(self):
        user = self.request.user
        return (user.is_authenticated and
               (user.profile.role == 'admin' or user.profile.is_super_admin))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Potrebujete administrátorské oprávnenia.')
            return redirect('profile', username=self.request.user.username)
        return super().handle_no_permission()


class WriterOrSuperAdminRequiredMixin(UserPassesTestMixin):
    """Writer or SuperAdmin"""
    def test_func(self):
        user = self.request.user
        return (user.is_authenticated and
               (user.profile.role == 'writer' or user.profile.is_super_admin))
