from django.test import TestCase
from django.utils import timezone
from .models import ActivityPost
from main.models import SocialUser
import datetime
from django.urls import reverse


# Create your tests here.
def create_post(title, description, status):
    # Status values:
    # 1: Draft
    # 2: Posted
    # 3: Archived
    time = timezone.now() + datetime.timedelta(days=0)
    return ActivityPost.objects.create(
        timestamp=time, title=title, description=description, status=status
    )


class TestHomePage(TestCase):
    def test_no_post(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts are available.")
        self.assertQuerysetEqual(response.context["latest_posts_list"], [])


class TestEditPost(TestCase):
    def setUp(self):
        # Create a test user
        self.user = SocialUser.objects.create_user(
            username="testuser", password="testpassword"
        )

        # Create a test post
        self.post = ActivityPost.objects.create(
            title="Test Post",
            description="Test Description",
            poster=self.user,
            status=ActivityPost.Status.DRAFT,
        )

        # Login the test user
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

    def test_edit_post_save_changes(self):
        # Simulate a POST request to save changes
        response = self.client.post(
            reverse("posts:edit_post_request", args=[self.post.id]),
            {
                "title": "Updated Title",
                "description": "Updated Description",
                "action": "save",
            },
        )

        # Check that the response is a redirect to the home page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:home"))

        # Refresh the post from the database
        updated_post = ActivityPost.objects.get(pk=self.post.id)

        # Check that the post has been updated as a draft
        self.assertEqual(updated_post.title, "Updated Title")
        self.assertEqual(updated_post.description, "Updated Description")
        self.assertEqual(updated_post.status, ActivityPost.Status.DRAFT)

    def test_edit_post_post(self):
        # Simulate a POST request to post the edited post
        response = self.client.post(
            reverse("posts:edit_post_request", args=[self.post.id]),
            {
                "title": "Updated Title",
                "description": "Updated Description",
                "action": "post",
            },
        )

        # Check that the response is a redirect to the home page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:home"))

        # Refresh the post from the database
        updated_post = ActivityPost.objects.get(pk=self.post.id)

        # Check that the post has been updated and is now active
        self.assertEqual(updated_post.title, "Updated Title")
        self.assertEqual(updated_post.description, "Updated Description")
        self.assertEqual(updated_post.status, ActivityPost.Status.ACTIVE)
