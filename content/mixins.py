from django.contrib.auth.mixins import UserPassesTestMixin


class ArticleOwnerMixin(UserPassesTestMixin):
    """Check if user owns the article (writer of bulletin or SuperAdmin)"""

    def test_func(self):
        article = self.get_object()
        user = self.request.user

        # SuperAdmin can access any article
        if not user.is_authenticated:
            return False

        # Writer can access their own articles
        if user.profile.is_super_admin:
            return True
        return article.bulletin == user.profile.bulletin


class BulletinOwnerMixin(UserPassesTestMixin):
    """Check if user owns the bulletin or is SuperAdmin"""

    def test_func(self):
        bulletin = self.get_object()
        user = self.request.user

        if not user.is_authenticated:
            return False

        # SuperAdmin can access any bulletin
        if user.profile.is_super_admin:
            return True

        # Writer can access their own bulletin
        return bulletin.owner == user.profile


class CanPromoteUsersMixin(UserPassesTestMixin):
    pass