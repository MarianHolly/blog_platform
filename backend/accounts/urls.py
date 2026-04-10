from django.urls import path

from accounts.views import SignUpView, logout_user, CustomLoginView, \
    ProfileDetailView, ProfileUpdateView, ProfileActivityView, \
    PromoteReaderToAdminView, PromoteReaderToWriterView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_user, name="logout", ),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/<str:username>/", ProfileDetailView.as_view(), name="profile"),
    path("profile/<str:username>/activity/", ProfileActivityView.as_view(), name="profile_activity"),
    path("profile/update/<str:username>/", ProfileUpdateView.as_view(), name="profile_update"),
    path("profile/promote/<str:username>/writer/", PromoteReaderToWriterView.as_view(), name="promote_to_writer"),
    path("profile/promote/<str:username>/admin/", PromoteReaderToAdminView.as_view(), name="promote_to_admin"),
]