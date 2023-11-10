from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("signup/", views.sign_up, name="signup"),
    path("profile/<int:pk>/", views.ProfileDetailsView.as_view(), name="profile"),
    path("profile/<int:pk>/notifications/", views.notifications, name="notifications"),
    # Connections
    path(
        "profile/<int:pk>/connections/",
        views.ProfileDetailsView.as_view(),
        name="connections",
    ),
    path(
        "profile/<int:pk>/request_connection/",
        views.request_connection,
        name="request_connection",
    ),
    path(
        "profile/<int:pk>/accept_connection/",
        views.accept_connection,
        name="accept_connection",
    ),
    path(
        "profile/<int:pk>/remove_connection/",
        views.remove_connection,
        name="remove_connection",
    ),
    # Search and Discovery
    path("discover/", views.DiscoverPageView.as_view(), name="discover"),
]
