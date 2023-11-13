from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("profile/new", views.ProfileCreationView.as_view(), name="new_profile"),
    # path("home/", views.home, name="home"),
    # path("signup/", views.sign_up, name="signup"),
    # path("create_profile/", views.CreateProfileView.as_view(), name="create_profile"),
    # path("profile/<int:pk>/", views.ProfileDetailsView.as_view(), name="profile"),
    # path("profile/<int:pk>/notifications/", views.notifications, name="notifications"),
    # # Connections
    # path(
    #     "profile/<int:pk>/connections/",
    #     views.connections,
    #     name="connections",
    # ),
    # path(
    #     "profile/<int:pk>/request_connection/",
    #     views.request_connection,
    #     name="request_connection",
    # ),
    # path(
    #     "profile/<int:pk>/cancel_connection_request/",
    #     views.cancel_connection_request,
    #     name="cancel_connection_request",
    # ),
    # path(
    #     "profile/<int:pk>/accept_connection/",
    #     views.accept_connection,
    #     name="accept_connection",
    # ),
    # path(
    #     "profile/<int:pk>/remove_connection/",
    #     views.remove_connection,
    #     name="remove_connection",
    # ),
    # # Search and Discovery
    # path("discover/", views.DiscoverPageView.as_view(), name="discover"),
    # path("delete-account/", views.delete_account, name="delete_account_request"),
]
