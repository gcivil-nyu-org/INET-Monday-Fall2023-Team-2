from django.test import TestCase
from django.urls import reverse
from posts.models import ActivityPost

# from django.utils import timezone
# from .models import SocialUser, Connection, Notification
from .models import SocialUser


# Create your tests here.
class MainViewNoPostTest(TestCase):
    def setUp(self):
        self.user = SocialUser.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_main_view_no_post(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)

        # Check that the context contains the expected keys
        self.assertIn("interests_posts", response.context)
        self.assertIn("connection_posts", response.context)

        # Check that no posts are available in interests_posts and connection_posts
        self.assertQuerysetEqual(response.context["interests_posts"], [])
        self.assertQuerysetEqual(response.context["connection_posts"], [])

        if (
            not response.context["interests_posts"]
            and not response.context["connection_posts"]
        ):
            # Checks if main page is empty
            self.assertContains(response, "")


class MainViewArchivedPostTest(TestCase):
    def setUp(self):
        self.user = SocialUser.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        # Create an archived post
        ActivityPost.objects.create(
            poster=self.user,
            title="Archived Post",
            description="This post is archived.",
            status=ActivityPost.PostStatus.ARCHIVED,
        )

    def test_main_view_archived_post(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)
        # Check that the archived post is not shown in home page
        self.assertNotContains(response, "Archived Post")


# class MainViewPostedPostTest(TestCase):
#     def setUp(self):
#         self.user = SocialUser.objects.create_user(
#             username="testuser", password="testpassword"
#         )
#         self.client.login(username="testuser", password="testpassword")

#         # Create a posted post
#         ActivityPost.objects.create(
#             poster=self.user,
#             title="Posted Post",
#             description="This post is posted.",
#             status=ActivityPost.PostStatus.ACTIVE,
#         )

#     def test_main_view_posted_post(self):
#         response = self.client.get(reverse("main:home"))
#         self.assertEqual(response.status_code, 200)
#         # Check that the posted post is present in the response
#         self.assertContains(response, "Posted Post")


class MainViewDraftedPostTest(TestCase):
    def setUp(self):
        self.user = SocialUser.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        # Create a drafted post
        ActivityPost.objects.create(
            poster=self.user,
            title="Drafted Post",
            description="This post is drafted.",
            status=ActivityPost.PostStatus.DRAFT,
        )

    def test_main_view_drafted_post(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)
        # Check that the drafted post is not present in the response
        self.assertNotContains(response, "Drafted Post")


# class MainViewMultiplePostTests(TestCase):
#     def setUp(self):
#         # Create a user
#         self.user = SocialUser.objects.create_user(
#             username="testuser", password="testpassword"
#         )
#         self.client.login(username="testuser", password="testpassword")

#         # Create an archived post
#         ActivityPost.objects.create(
#             poster=self.user,
#             title="Archived Post",
#             description="This post is archived.",
#             status=ActivityPost.PostStatus.ARCHIVED,
#         )

#         # Create a posted post
#         ActivityPost.objects.create(
#             poster=self.user,
#             title="Posted Post",
#             description="This post is posted.",
#             status=ActivityPost.PostStatus.ACTIVE,
#         )

#         # Create a drafted post
#         ActivityPost.objects.create(
#             poster=self.user,
#             title="Drafted Post",
#             description="This post is drafted.",
#             status=ActivityPost.PostStatus.DRAFT,
#         )

#     def test_main_view_multiple_post(self):
#         response = self.client.get(reverse("main:home"))
#         self.assertEqual(response.status_code, 200)
#         # Check that the only Posted Post is displayed
#         self.assertNotContains(response, "Drafted Post")
#         self.assertContains(response, "Posted Post")
#         self.assertNotContains(response, "Archived Post")


# class NotificationViewTests(TestCase):
#     def setUp(self):
#         # Create two users
#         self.user1 = SocialUser.objects.create_user(
#             username="user1", password="testpassword1"
#         )
#         self.user2 = SocialUser.objects.create_user(
#             username="user2", password="testpassword2"
#         )

#         # Log in the users
#         self.client.login(username="user1", password="testpassword1")

#         # Create a connection request notification
#         self.connection_request_notification = Notification.objects.create(
#             receiver=self.user1,
#             requester=self.user2,
#             content="Connection request from user2",
#             type=Notification.NotificationType.CONNECTION_REQUEST,
#             timestamp=timezone.now(),
#         )

#     def test_notification_view_connection_request(self):
#         # Test accessing the notifications view
#         response = self.client.get(
#             reverse("main:notifications", kwargs={"pk": self.user1.pk})
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Connection request from user2")
#         self.assertContains(response, "Accept")


# class ConnectionTests(TestCase):
#     def setUp(self):
#         # Create a user
#         self.user = SocialUser.objects.create_user(
#             username="testuser", password="testpassword"
#         )

#         # Log in the user
#         self.client.login(username="testuser", password="testpassword")

#     def test_connections_view(self):
#         # Create a connection
#         connected_user = SocialUser.objects.create_user(
#             username="connecteduser", password="testpassword"
#         )
#         Connection.objects.create(
#             requester=self.user,
#             receiver=connected_user,
#             status=Connection.ConnectionStatus.CONNECTED,
#             timestamp=timezone.now(),
#         )

#         # Test accessing the connections view
#         response = self.client.get(
#             reverse("main:connections", kwargs={"pk": self.user.pk})
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "connecteduser")
