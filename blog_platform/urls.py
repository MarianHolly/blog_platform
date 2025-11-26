from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from content.views import *

# Customize Django Admin Site
admin.site.site_header = "Blog Platform Admin"
admin.site.site_title = "Blog Platform Administration"
admin.site.index_title = "Spravovací panel"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("content.urls")),
    path("accounts/", include("accounts.urls") ),
    path('', include('engagement.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)