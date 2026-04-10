from django.contrib.auth.mixins import UserPassesTestMixin


class ArticleOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        article = self.get_object()
        return self.request.user.profile.role == 'writer' and article.bulletin == self.request.user.profile.bulletin
