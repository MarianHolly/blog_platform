from django.urls import path

from accounts.views import ProfileDetailView
from content.views import HomePageView, AboutPageView, \
    ArticleListView, ArticleDetailView, ArticleUpdateView, ArticleCreateView, ArticleDeleteView, \
    BulletinDetailView, BulletinUpdateView, BulletinDashboardView, \
    SubscriptionToggleView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),

    path("articles/", ArticleListView.as_view(), name="article_list"),
    path("article/<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
    path("article/create/", ArticleCreateView.as_view(), name="article_create"),
    path("article/edit/<int:pk>/", ArticleUpdateView.as_view(), name="article_edit"),
    path("article/delete/<int:pk>/", ArticleDeleteView.as_view(), name='article_delete'),

    path("bulletin/<slug:slug>/", BulletinDetailView.as_view(), name="bulletin_detail"),
    path("bulletin/<slug:slug>/edit/", BulletinUpdateView.as_view(), name="bulletin_edit"),
    path("bulletin/<slug:slug>/dashboard/", BulletinDashboardView.as_view(), name="bulletin_dashboard"),

    path("subscribe/<slug:slug>/", SubscriptionToggleView.as_view(), name="toggle_subscription"),
]