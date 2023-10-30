from django.test import TestCase
from django.utils import timezone
from .models import ActivityPost
from socialuser.models import SocialUser
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
        self.user = SocialUser.objects.create(
            user_id="test_user_id",
            name="Test User",
            pronouns="she/her"
        )

        # Create a test post associated with the current user
        self.post = ActivityPost.objects.create(
            title="Test Title1",
            description="Test Description1",
            social_user=self.user
        )

    def test_edit_post_saves(self):
        response = self.client.post(
            reverse("posts:edit_post_request", args=[self.post.id]),
            data={"title": "New Title", "description": "New Description", "action": "save"})
        # Check if the response redirects to the home page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

        # Check if the post has been updated
        updated_post = ActivityPost.objects.get(pk=self.post.id)
        self.assertEqual(updated_post.title, "New Title")
        self.assertEqual(updated_post.description, "New Description")
        if updated_post:
            print("Post updated successfully!")
        else:
            print("Post editing failed.")
