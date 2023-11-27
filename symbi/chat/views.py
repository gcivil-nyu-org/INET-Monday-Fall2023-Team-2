from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
import django.views.generic as generic

from .models import ChatRoom, Message
from main.models import SocialUser


class ChatRoomListView(generic.ListView):
    model = ChatRoom
    template_name = "chat/chat_room_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chat_rooms"] = ChatRoom.get_chatrooms(self.request.user)
        return context


class ChatRoomView(generic.DetailView):
    model = ChatRoom
    template_name = "chat/chat_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = Message.get_messages(self.object)
        return context

    def post(self, request, *args, **kwargs):
        message = request.POST.get("message")
        chat_room = get_object_or_404(ChatRoom, pk=kwargs["pk"])
        Message.objects.create(
            sender=request.user, chat_room=chat_room, content=message
        )
        return redirect("chat:chat_room", pk=chat_room.pk)


class ChatRoomCreateView(generic.View):
    def get(self, request, *args, **kwargs):
        requester = get_object_or_404(SocialUser, username=self.kwargs["requester"])
        receiver = get_object_or_404(SocialUser, username=self.kwargs["receiver"])

        existing_chat = (
            ChatRoom.objects.filter(members=requester).filter(members=receiver).first()
        )

        if existing_chat:
            print("one exists")
            return redirect(
                reverse_lazy("chat:chat_room", kwargs={"pk": existing_chat.pk})
            )
        else:
            new_chat = ChatRoom.objects.create(creator=requester)
            new_chat.members.add(requester)
            new_chat.members.add(receiver)
            return redirect(reverse_lazy("chat:chat_room", kwargs={"pk": new_chat.pk}))
