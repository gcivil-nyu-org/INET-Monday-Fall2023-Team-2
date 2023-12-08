from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
import django.views.generic as generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from pusher import Pusher

from .models import ChatRoom, Message
from main.models import SocialUser

pusher = Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
)


@method_decorator(login_required, name="dispatch")
class ChatRoomListView(LoginRequiredMixin, generic.ListView):
    model = ChatRoom
    template_name = "chat/chat_room_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chat_rooms"] = ChatRoom.get_chatrooms(self.request.user)
        return context


def get_message_html(request):
    message_sender = request.GET.get("type")
    message_id = request.GET.get("content")
    message = Message.objects.get(pk=message_id)
    context = {"message": message, "user": request.user}
    if message_sender == request.user.username:
        html = render_to_string("chat/user_message.html", context)
    else:
        html = render_to_string("chat/member_message.html", context)
    return HttpResponse(html)


@method_decorator(login_required, name="dispatch")
class ChatRoomView(LoginRequiredMixin, generic.DetailView):
    model = ChatRoom
    template_name = "chat/chat_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = Message.get_messages(self.object)
        context["current_user"] = self.request.user.username
        return context

    def post(self, request, *args, **kwargs):
        message_text = request.POST.get("message")
        chat_room = get_object_or_404(ChatRoom, pk=kwargs["pk"])
        new_message = Message(
            chat_room=chat_room, sender=request.user, content=message_text
        )
        new_message.save()
        pusher.trigger(
            "chat",
            "message",
            {
                "id": new_message.id,
                "message": new_message.content,
                "username": new_message.sender.username,
                "chat_room": new_message.chat_room.id,
                "created": new_message.created.strftime("%b %d %Y, %I:%M %p"),
            },
        )
        return JsonResponse({"success": "Message sent successfully"})

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
        if self.request.user.username != requester.username:
            # returns 403 Forbidden page
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
