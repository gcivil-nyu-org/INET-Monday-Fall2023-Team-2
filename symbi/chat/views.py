from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render
from django.contrib.auth import login

from .models import ChatRoom, Message


class ChatPageView(generic.ListView):
    model = Message
    template_name = "chat/chat_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_user"] = self.request.user
        context["rooms"] = ChatRoom.objects.all()
        context["messages"] = Message.objects.all()
        return context
