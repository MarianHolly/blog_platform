from django.urls import path

from content.views import HomePageView, AboutPageView, ArticleListView, ArticleDetailView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("articles/", ArticleListView.as_view(), name="article_list"),
    path("article/<int:pk>", ArticleDetailView.as_view(), name="article_detail"),
]