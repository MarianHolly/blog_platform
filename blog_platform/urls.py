from django.contrib import admin
from django.urls import path, include

from content.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("content.urls")),
    path("accounts/", include("accounts.urls") ),
]
