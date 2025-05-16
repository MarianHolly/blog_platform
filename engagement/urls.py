from django.urls import path

from engagement.views import LikeToggleView, ReadLaterToggleView

urlpatterns = [
    path("like/<int:id>/", LikeToggleView.as_view(), name="toggle_like"),
    path("read-later/<int:id>/", ReadLaterToggleView.as_view(), name="toggle_read_later"),
]