from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("signup/", views.sign_up, name="signup"),
    path("profile/<int:pk>/", views.ProfileDetailsView.as_view(), name="profile"),

    # Search and Discovery
    path("discover/", views.DiscoverPageView.as_view(), name="discover")
]
