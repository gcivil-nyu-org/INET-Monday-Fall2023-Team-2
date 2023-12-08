from django.test import TestCase
from django.urls import reverse, reverse_lazy
from posts.models import ActivityPost
from django.contrib.auth import authenticate

# from django.utils import timezone
# from .models import SocialUser, Connection, Notification
from .models import SocialUser


class LandingPageViewTest(TestCase):
    def setUp(self):
        self.testuser = SocialUser.objects.create_user(
            username="testuser", email="testuser@nyu.edu", password="testpassword"
        )

    def test_authenticated_user(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse_lazy("main:landing"))
        # Checks if properly redirects to home when logged in
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse_lazy("main:home"))

    def test_unauthenticated_user(self):
        response = self.client.get(reverse_lazy("main:landing"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/landing.html")


class LoginViewTest(TestCase):
    def setUp(self):
        self.testuser = SocialUser.objects.create_user(
            username="testuser", email="testuser@nyu.edu", password="testpassword"
        )

    def test_login_template(self):
        response = self.client.get(reverse_lazy("main:login"))

        # Check if properly shows login template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/login.html")

    def test_login_form_invalid(self):
        response = self.client.post(
            reverse_lazy("main:login"),
            {"username": "testuser", "password": "wrongpassword"},
        )

        # Check that the user isn't redirected to home
        self.assertEqual(response.status_code, 200)

        # Check that error messages are shown
        self.assertContains(
            response,
            "Please enter a correct username and password. Note that both fields may be case-sensitive.",
        )

    def test_login_form_valid(self):
        response = self.client.post(
            reverse_lazy("main:login"),
            {"username": "testuser", "password": "testpassword"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy("main:home"))


class SignupViewTest(TestCase):
    def test_signup_template(self):
        response = self.client.get(reverse_lazy("main:signup"))

        # Check if properly shows signup template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/signup.html")

    def test_signup_form_valid(self):
        user_data = {
            "username": "testuser",
            "email": "testuser@nyu.edu",
            "full_name": "test user",
            "pronouns": SocialUser.Pronouns.HE,
            "date_of_birth": "1990-01-01",
            "major": "Computer Science",
            "interests": [],
            "password1": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(reverse_lazy("main:signup"), user_data)

        # Check if redirected to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy("main:home"))

        # Check that the user is added to the database
        self.assertTrue(SocialUser.objects.filter(username="testuser").exists())

        # Check that the user is logged in
        logged_in_user = authenticate(username="testuser", password="testpass123")
        self.assertIsNotNone(logged_in_user)
        self.assertTrue(logged_in_user.is_authenticated)

    def test_signup_form_invalid(self):
        response = self.client.post(reverse_lazy("main:signup"), {})

        # Check that the user isn't redirected to home
        self.assertEqual(response.status_code, 200)

        # Check that error messages are shown
        self.assertContains(
            response,
            "This field is required.",
        )


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
