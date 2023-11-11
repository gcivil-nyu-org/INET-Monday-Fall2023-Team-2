from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("signup/", views.sign_up, name="signup"),
    path("create_profile/", views.CreateProfileView.as_view(), name="create_profile"),
    path("profile/<int:pk>/", views.ProfileDetailsView.as_view(), name="profile"),
    # Search and Discovery
    path("discover/", views.DiscoverPageView.as_view(), name="discover"),
    path("delete-account/", views.delete_account, name="delete_account_request"),
]
