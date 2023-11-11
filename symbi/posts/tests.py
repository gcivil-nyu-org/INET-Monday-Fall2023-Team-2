from django.test import TestCase
from django.utils import timezone
from .models import ActivityPost, Comment
from main.models import SocialUser
import datetime
from django.urls import reverse
from django.contrib.auth import get_user_model


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
            first_name="Test User", pronouns=SocialUser.Pronouns.SHE
        )

        # Create a test post associated with the current user
        self.post = ActivityPost.objects.create(
            title="Test Title1", description="Test Description1", poster=self.user
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


class CommentsTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="TestPassword!23"
        )
        self.post = ActivityPost.objects.create(
            title="Test Post", description="Test Description", poster=self.user
        )

    def test_comment_creation(self):
        # Log in the user
        self.client.login(username="testuser", password="TestPassword!23")

        # Comment data
        comment_text = "This is a test comment"

        # Post a comment
        response = self.client.post(
            reverse("posts:add_comment", args=[self.post.id]), {"comment": comment_text}
        )
        self.assertEqual(
            response.status_code, 302
        )  # Check if the comment was successfully posted

        # Check if the comment is in the database
        comment = Comment.objects.get(
            post=self.post,
            commentPoster=self.user,
            text=comment_text,
        )
        self.assertIsNotNone(comment)

    def test_comment_deletion(self):
        # Create a comment
        comment = Comment.objects.create(
            post=self.post,
            commentPoster=self.user,
            text="Test Comment",
            timestamp=timezone.now(),
        )

        print("Starting test_comment_deletion")
        print("Comment ID:", comment.id)

        # Log in the user
        self.client.login(username="testuser", password="TestPassword!23")

        # Delete a comment
        response = self.client.post(
            reverse("posts:delete_comment", args=[self.post.id, comment.id])
        )
        self.assertEqual(
            response.status_code, 302
        )  # Check if the comment was successfully deleted

        # Check if the comment is no longer in the database
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(pk=comment.id)
