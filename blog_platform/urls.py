from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from content.views import *


def health_check(request):
    return JsonResponse({"status": "ok"})

# Customize Django Admin Site
admin.site.site_header = "Blog Platform Admin"
admin.site.site_title = "Blog Platform Administration"
admin.site.index_title = "Spravovací panel"

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # ============================================================================
    # REST API v1
    # ============================================================================
    path('api/v1/', include([
        # JWT Authentication
        # POST /api/v1/auth/token/ - Get access + refresh tokens
        # POST /api/v1/auth/token/refresh/ - Get new access token
        path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

        # Content Resources
        # /api/v1/articles/, /api/v1/bulletins/, /api/v1/subscriptions/
        path('', include('content.api_urls')),

        # Engagement Resources
        # /api/v1/comments/, /api/v1/bookmarks/
        path('', include('engagement.api_urls')),

        # API Documentation (Swagger UI)
        # GET /api/v1/schema/ - OpenAPI schema (JSON)
        # GET /api/v1/docs/ - Interactive Swagger documentation
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ])),

    # ============================================================================
    # Traditional Django Views (HTML templates)
    # ============================================================================
    path("", include("content.urls")),
    path("accounts/", include("accounts.urls")),
    path('', include('engagement.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)