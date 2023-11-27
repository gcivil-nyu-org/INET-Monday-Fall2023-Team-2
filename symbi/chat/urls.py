from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path("", views.ChatRoomListView.as_view(), name="chat_room_list"),
    path("<int:pk>/", views.ChatRoomView.as_view(), name="chat_room"),
    path(
        "new/<slug:requester>/<slug:receiver>/",
        views.ChatRoomCreateView.as_view(),
        name="chat_room_create",
    ),
]
