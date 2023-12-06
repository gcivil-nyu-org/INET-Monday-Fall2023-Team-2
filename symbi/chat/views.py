from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
import django.views.generic as generic

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ChatRoom, Message
from main.models import SocialUser


@method_decorator(login_required, name="dispatch")
class ChatRoomListView(LoginRequiredMixin, generic.ListView):
    model = ChatRoom
    template_name = "chat/chat_room_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chat_rooms"] = ChatRoom.get_chatrooms(self.request.user)
        return context


@method_decorator(login_required, name="dispatch")
class ChatRoomView(LoginRequiredMixin, generic.DetailView):
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
        
            
    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user can access the page being requested
        chat_room = get_object_or_404(ChatRoom, pk=kwargs["pk"])
        if not chat_room.members.filter(username=self.request.user.username).exists():
            # returns 403 Forbidden page
            return self.handle_no_permission()
            
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class ChatRoomCreateView(LoginRequiredMixin, generic.View):
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
            
    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user can access the page being requested
        requester = get_object_or_404(SocialUser, username=self.kwargs["requester"])
        receiver = get_object_or_404(SocialUser, username=self.kwargs["receiver"])
        if self.request.user.username != requester.username:
            # returns 403 Forbidden page
            return self.handle_no_permission()
            
        return super().dispatch(request, *args, **kwargs)
