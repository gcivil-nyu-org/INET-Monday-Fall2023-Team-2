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
    user = SocialUser.objects.create(
        user_id="test_user_id", name="Test User", pronouns="she/her"
    )
    return ActivityPost.objects.create(
        timestamp=time,
        title=title,
        description=description,
        status=status,
        social_user=user,
    )


class TestHomePage(TestCase):
    def test_no_post(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts are available.")
        self.assertQuerysetEqual(response.context["latest_posts_list"], [])

    def test_draft_post(self):
        draftPost = create_post("test1", "testing1", 1)
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, draftPost.title)

    def test_posted_post(self):
        postedPost = create_post("test2", "testing1", 2)
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, postedPost.title)

    def test_archived_post(self):
        archivedPost = create_post("test3", "testing1", 3)
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, archivedPost.title)

    def test_all_three_status_post(self):
        draftPost = create_post("test1", "testing1", 1)
        postedPost = create_post("test2", "testing1", 2)
        archivedPost = create_post("test3", "testing1", 3)
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, draftPost.title)
        self.assertContains(response, postedPost.title)
        self.assertNotContains(response, archivedPost.title)


class TestEditPost(TestCase):
    def setUp(self):
        # Create a test user
        self.user = SocialUser.objects.create(
            user_id="test_user_id", name="Test User", pronouns="she/her"
        )

        # Create a test post associated with the current user
        self.post = ActivityPost.objects.create(
            title="Test Title1", description="Test Description1", social_user=self.user
        )

    def test_edit_post_saves(self):
        response = self.client.post(
            reverse("posts:edit_post_request", args=[self.post.id]),
            data={
                "title": "New Title",
                "description": "New Description",
                "action": "save",
            },
        )
        # Check if the response redirects to the home page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:home"))

        # Check if the post has been updated
        updated_post = ActivityPost.objects.get(pk=self.post.id)
        self.assertEqual(updated_post.title, "New Title")
        self.assertEqual(updated_post.description, "New Description")
        if updated_post:
            print("Post updated successfully!")
        else:
            print("Post editing failed.")
