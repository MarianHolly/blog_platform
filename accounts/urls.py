from django.urls import path

from accounts.views import SignUpView, logout_user, CustomLoginView, \
    ProfileDetailView, ProfileUpdateView, ProfileRolePromoteView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_user, name="logout", ),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/<str:username>/", ProfileDetailView.as_view(), name="profile"),
    path("profile/update/<str:username>/", ProfileUpdateView.as_view(), name="profile_update"),
    path("profile/promote/<str:username>/", ProfileRolePromoteView.as_view(), name="promote_to_reader"),
]