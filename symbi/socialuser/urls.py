from django.urls import path

from . import views

app_name = "socialuser"
urlpatterns = [
    path("create-profile/", views.CreateProfileView.as_view(), name="create_profile"),
    path("profile/<int:pk>/", views.ProfileDetailsView.as_view(), name="profile_view"),
]
