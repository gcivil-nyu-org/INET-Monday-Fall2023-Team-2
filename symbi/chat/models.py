from django.db import models

from main.models import SocialUser


class ChatRoom(models.Model):
    creator = models.ForeignKey(
        SocialUser, on_delete=models.CASCADE, related_name="creator"
    )
    members = models.ManyToManyField(SocialUser, related_name="members")
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.creator.username


class Message(models.Model):
    chat_room = models.ForeignKey("chat.ChatRoom", on_delete=models.CASCADE)
    sender = models.ForeignKey("main.SocialUser", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
