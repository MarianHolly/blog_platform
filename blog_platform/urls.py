from django.contrib import admin
from django.urls import path

from content.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    # Essential Urls
    path("", home, name="home"),
    path("about/", about, name="about"),
    path("article/<int:pk>", ArticleDetailView.as_view(), name="article"),
]
