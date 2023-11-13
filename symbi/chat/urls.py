from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("chat/", views.ChatPageView.as_view(), name="chat_page"),
]
