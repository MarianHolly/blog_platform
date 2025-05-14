from django.urls import path

from engagement.views import LikeToggleView

urlpatterns = [
    path("like/<int:id>/", LikeToggleView.as_view(), name="toggle_like"),
]