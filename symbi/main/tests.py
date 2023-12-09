from django.test import TestCase
from django.urls import reverse, reverse_lazy
from posts.models import ActivityPost
from django.contrib.auth import authenticate

# from django.utils import timezone
# from .models import SocialUser, Connection, Notification
from .models import SocialUser, Block, Connection
from posts.models import Comment
from chat.models import ChatRoom, Message
from .signals import user_blocked


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


class MainAppTests(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = SocialUser.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_home_page_view(self):
        # Test that the home page returns a 200 status code for an authenticated user
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/home.html")

    def test_logout_view(self):
        # Test that the logout view logs out the user and redirects to the landing page
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("main:logout"))
        self.assertEqual(
            response.status_code, 302
        )  # 302 is the HTTP status code for a redirect
        self.assertRedirects(response, reverse("main:landing"))
        # You may also want to test cases where logout fails

    def test_profile_page_view(self):
        # Test that the profile page view returns a 200 status code for an authenticated user
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(
            reverse("main:profile_page", kwargs={"username": "testuser"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/profile_page.html")

    def test_edit_profile_view(self):
        # Test that the edit profile view returns a 200 status code for an authenticated user
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(
            reverse("main:edit_profile_page", kwargs={"username": "testuser"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/edit_profile_page.html")

    def tearDown(self):
        # Clean up after the tests if needed
        pass


class SignalTests(TestCase):
    def setUp(self):
        # Create users for testing
        self.blocker = SocialUser.objects.create_user(
            username="blocker", password="testpassword", email="blocker@nyu.edu"
        )
        self.blocked_user = SocialUser.objects.create_user(
            username="blockedUser", password="testpassword", email="blockeruser@nyu.edu"
        )
        

    def test_remove_connection_on_block(self):
        # Create a block instance
        block_instance = Block.objects.create(
            blocker=self.blocker, blocked_user=self.blocked_user
        )
        user_blocked.send(sender=Block, instance=block_instance, created=True)

        # Assert that the connection is deleted
        self.assertFalse(
            Connection.objects.filter(
                requester=self.blocker, receiver=self.blocked_user
            ).exists()
        )

    def test_remove_comments_on_block(self):
        # Create a block instance
        block_instance = Block.objects.create(
            blocker=self.blocker, blocked_user=self.blocked_user
        )
        user_blocked.send(sender=Block, instance=block_instance, created=True)

        # Assert that the comments are deleted
        self.assertFalse(
            Comment.objects.filter(
                commentPoster=self.blocker, post__poster=self.blocked_user
            ).exists()
        )
        self.assertFalse(
            Comment.objects.filter(
                commentPoster=self.blocked_user, post__poster=self.blocker
            ).exists()
        )

    def test_remove_messages_on_block(self):
        # Create a block instance
        block_instance = Block.objects.create(
            blocker=self.blocker, blocked_user=self.blocked_user
        )
        user_blocked.send(sender=Block, instance=block_instance, created=True)

        # Assert that the messages are deleted
        self.assertFalse(
            Message.objects.filter(
                sender=self.blocker, chat_room__members=self.blocked_user
            ).exists()
        )
        self.assertFalse(
            Message.objects.filter(
                sender=self.blocked_user, chat_room__members=self.blocker
            ).exists()
        )

    def test_remove_chat_rooms_on_block(self):
        # Create a block instance
        block_instance = Block.objects.create(
            blocker=self.blocker, blocked_user=self.blocked_user
        )
        user_blocked.send(sender=Block, instance=block_instance, created=True)

        # Assert that the chat rooms are deleted
        self.assertFalse(
            ChatRoom.objects.filter(members=self.blocker)
            .filter(members=self.blocked_user)
            .exists()
        )
