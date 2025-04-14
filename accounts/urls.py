from django.urls import path

from accounts.views import SignUpView, logout_user, ProfileDetailView, CustomLoginView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_user, name="logout", ),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/<str:username>/", ProfileDetailView.as_view(), name="profile"),
    # path("profile/edit", ProfileUpdateView)
]