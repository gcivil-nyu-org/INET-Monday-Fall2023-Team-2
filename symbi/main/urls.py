from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    # path("", views.home, name="home"),
    # path("home/", views.home, name="home"),
    # path("signup/", views.sign_up, name="signup"),
    # path("profile/<int:pk>/", views.ProfileDetailsView.as_view(), name="profile"),
    path("profile/new", views.ProfileCreationView.as_view(), name="create_profile"),
]
