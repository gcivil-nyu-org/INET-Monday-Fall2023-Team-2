from django.contrib import admin

from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ["creator", "start_date"]
    search_fields = ["creator", "members"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["chat_room", "sender", "content", "timestamp"]
    search_fields = ["chat_room", "sender", "content"]
