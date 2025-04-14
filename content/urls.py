from django.urls import path

from content.views import HomePageView, AboutPageView, ArticleListView, ArticleDetailView, ArticleUpdateView, \
    ArticleCreateView, ArticleDeleteView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("articles/", ArticleListView.as_view(), name="article_list"),
    path("article/<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
    path("article/create/", ArticleCreateView.as_view(), name="article_create"),
    path("article/edit/<int:pk>/", ArticleUpdateView.as_view(), name="article_edit"),
    path("article/delete/<int:pk>/", ArticleDeleteView.as_view(), name='article_delete'),

]