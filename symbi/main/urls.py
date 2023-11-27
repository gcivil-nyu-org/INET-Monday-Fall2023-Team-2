from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("home/", views.HomePageView.as_view(), name="home"),
    path(
        "profile/<slug:username>", views.ProfilePageView.as_view(), name="profile_page"
    ),
    path(
        "profile/<slug:username>/edit",
        views.EditProfileView.as_view(),
        name="edit_profile_page",
    ),
    path("profile/<int:pk>/notifications/", views.notifications, name="notifications"),
    # Connections
    path(
        "connections/<slug:username>",
        views.ConnectionsPageView.as_view(),
        name="connections",
    ),
    path(
        "connection/accept/<slug:requester>/<slug:receiver>",
        views.AcceptConnectionView.as_view(),
        name="accept_connection",
    ),
    path(
        "connection/request/<slug:receiver>",
        views.RequestConnectionView.as_view(),
        name="request_connection",
    ),
    path(
        "connection/cancel/<slug:requester>/<slug:receiver>",
        views.CancelConnectionView.as_view(),
        name="cancel_connection",
    ),
    path(
        "connections/<slug:username>",
        views.ConnectionsPageView.as_view(),
        name="connections",
    ),
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
    # Search and Discovery
    path("discover/", views.DiscoverPageView.as_view(), name="discover"),
    # path("discover/", views.search_view, name="discover"),
    path("delete-account/", views.delete_account, name="delete_account_request"),
]
