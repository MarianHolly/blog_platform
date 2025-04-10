from django.contrib.auth.views import LoginView
from django.urls import path

from accounts.views import SignUpView, logout_user, ProfileDetailView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_user, name="logout", ),
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile"),
]