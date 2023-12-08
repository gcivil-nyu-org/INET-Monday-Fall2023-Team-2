from django.dispatch import Signal, receiver
from django.db.models.signals import post_save
from .models import Block, Connection
from posts.models import Comment
from chat.models import ChatRoom, Message

# restrictions imposed on a blocked_user by implementing two actions:
#   1. Removing all existing communications between blocker and blocked_user
#   2. Preventing further interactions between blocker and blocked_user by hiding the blocker’s activities

user_blocked = Signal()


@receiver(post_save, sender=Block)
def remove_existing_communications(instance, created, **kwargs):
    if created:
        blocker = instance.blocker
        blocked_user = instance.blocked_user

        # Remove connections
        # Check if users are connected
        is_connected = Connection.are_connected(blocker, blocked_user)

        if is_connected:
            connection = Connection.get_connection(blocker, blocked_user)

            # Cancel the connection request if it exists, delete notification
            if connection.status == "requested":
                if connection.notification:
                    connection.notification.delete()

            # Delete the connection, regardless of its status
            connection.delete()

        # Remove comments
        comments = Comment.objects.filter(
            commentPoster=blocker, post__poster=blocked_user
        ) | Comment.objects.filter(commentPoster=blocked_user, post__poster=blocker)
        comments.delete()

        # Handle chat restrctions
        # Get all ChatRooms where blocker and blocked_user are both members
        chat_rooms = ChatRoom.objects.filter(members=blocker).filter(
            members=blocked_user
        )

        for chat_room in chat_rooms:
            # ChatRoom is a group chat
            if chat_room.members.count() >= 3:
                # blocker is the creator of ChatRoom
                if chat_room.creator == blocker:
                    # Delete blocked user's messages
                    messages = Message.get_messages(chat_room).filter(
                        sender=blocked_user
                    )
                    messages.delete()
                    # Remove blocked_user from ChatRoom
                    chat_room.members.remove(blocked_user)
                else:
                    # Delete blocker's messages
                    messages = Message.get_messages(chat_room).filter(sender=blocker)
                    messages.delete()
                    # Remove blocker from ChatRoom
                    chat_room.members.remove(blocker)
            else:  # ChatRoom is a DirectMessage
                chat_room.delete()
