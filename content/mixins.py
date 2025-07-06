from django.contrib.auth.mixins import UserPassesTestMixin


class ArticleOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            article = self.get_object()
            user = self.request.user

            if not user.is_authenticated:
                return False

            # Admin can access anything
            if user.profile.is_admin:
                return True

            # Owner can access their own content
            return article.bulletin.owner == user.profile
        except:
            return False


class BulletinOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        try:
            bulletin = self.get_object()
            user = self.request.user

            if not user.is_authenticated:
                return False

            # Admin can access anything
            if user.profile.is_admin:
                return True

            # Owner can access their own bulletin
            return bulletin.owner == user.profile
        except:
            return False