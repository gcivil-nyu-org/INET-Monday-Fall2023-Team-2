from django.test import TestCase
from django.urls import reverse

from .models import ChatRoom, Message
from main.models import SocialUser


class ChatRoomListViewTestCase(TestCase):
    def setUp(self):
        self.user1 = SocialUser.objects.create_user(
            username="user1", email="testEmail1@nyu.edu", password="testPassword"
        )
        self.user2 = SocialUser.objects.create_user(
            username="user2", email="testEmail2@nyu.edu", password="testPassword"
        )
        self.chat_room = ChatRoom.objects.create(creator=self.user1)
        self.chat_room.members.set([self.user1, self.user2])

    def test_login_required(self):
        # Check if redirected to login page if not logged in
        response = self.client.get(reverse("chat:chat_room_list"))
        self.assertEqual(response.status_code, 302)

        # Check that user can properly view chat room list
        self.client.login(username="user1", password="testPassword")
        response = self.client.get(reverse("chat:chat_room_list"))
        self.assertEqual(response.status_code, 200)

    def test_context_data(self):
        self.client.login(username="user1", password="testPassword")

        # Access the view and check if the chat_rooms are in the context
        response = self.client.get(reverse("chat:chat_room_list"))
        self.assertEqual(response.status_code, 200)

        # Check if the chat_rooms in the context match the ones created in setUp
        chat_rooms_in_context = response.context["chat_rooms"]
        self.assertQuerysetEqual(chat_rooms_in_context, [self.chat_room], ordered=False)

        # Check if the chat_room is in the context and has the correct members
        self.assertIn("chat_rooms", response.context)
        chat_room = chat_rooms_in_context[0]
        self.assertEqual(chat_room.creator, self.user1)
        self.assertIn(self.user1, chat_room.members.all())
        self.assertIn(self.user2, chat_room.members.all())


class ChatRoomViewTestCase(TestCase):
    def setUp(self):
        self.user1 = SocialUser.objects.create_user(
            username="user1", email="testEmail1@nyu.edu", password="testPassword"
        )
        self.user2 = SocialUser.objects.create_user(
            username="user2", email="testEmail2@nyu.edu", password="testPassword"
        )
        self.chat_room = ChatRoom.objects.create(creator=self.user1)
        self.chat_room.members.set([self.user1, self.user2])

    def test_get_context_data(self):
        self.client.login(username="user1", password="testPassword")

        # Create a message for the chat room
        message_content = "Test message content"
        message = Message.objects.create(
            chat_room=self.chat_room, sender=self.user1, content=message_content
        )

        # Access the view and check if the messages are in the context
        response = self.client.get(
            reverse("chat:chat_room", kwargs={"pk": self.chat_room.pk})
        )
        self.assertEqual(response.status_code, 200)

        messages_in_context = response.context["messages"]
        self.assertQuerysetEqual(messages_in_context, [message], ordered=False)

    def test_post_method(self):
        self.client.login(username="user1", password="testPassword")

        # Simulate a POST request to add a new message
        message_text = "New message text"
        response = self.client.post(
            reverse("chat:chat_room", kwargs={"pk": self.chat_room.pk}),
            {"message": message_text},
        )

        # self.assertEqual(
        #     response.status_code, 302
        # )  # Expecting a redirect after posting a message

        # Check if the new message is added to the chat room
        new_message = Message.objects.last()
        self.assertEqual(new_message.chat_room, self.chat_room)
        self.assertEqual(new_message.sender, self.user1)
        self.assertEqual(new_message.content, message_text)


class ChatRoomCreateViewTestCase(TestCase):
    def setUp(self):
        self.user1 = SocialUser.objects.create_user(
            username="user1", email="testEmail1@nyu.edu", password="testPassword"
        )
        self.user2 = SocialUser.objects.create_user(
            username="user2", email="testEmail2@nyu.edu", password="testPassword"
        )

    def test_get_existing_chat_room(self):
        # Create an existing chat room between user1 and user2
        existing_chat = ChatRoom.objects.create(creator=self.user1)
        existing_chat.members.set([self.user1, self.user2])

        # Log in user1 and try to create a chat room with user2
        self.client.login(username="user1", password="testPassword")
        url = reverse(
            "chat:chat_room_create", kwargs={"requester": "user1", "receiver": "user2"}
        )
        response = self.client.get(url)

        # Expect a redirect to the existing chat room
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("chat:chat_room", kwargs={"pk": existing_chat.pk})
        )

    def test_get_new_chat_room(self):
        # Log in user1 and try to create a new chat room with user2
        self.client.login(username="user1", password="testPassword")
        url = reverse(
            "chat:chat_room_create", kwargs={"requester": "user1", "receiver": "user2"}
        )
        response = self.client.get(url)

        # Expect a redirect to the newly created chat room
        self.assertEqual(response.status_code, 302)
        new_chat = (
            ChatRoom.objects.filter(members=self.user1)
            .filter(members=self.user2)
            .first()
        )
        self.assertIsNotNone(new_chat)
        self.assertRedirects(
            response, reverse("chat:chat_room", kwargs={"pk": new_chat.pk})
        )
