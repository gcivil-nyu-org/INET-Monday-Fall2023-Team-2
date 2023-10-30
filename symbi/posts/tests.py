from django.test import TestCase
from django.utils import timezone
from .models import ActivityPost
import datetime


# Create your tests here.
def create_post(title, description, status):
    # Status values:
    # 1: Draft
    # 2: Posted
    # 3: Archived
    time = timezone.now() + datetime.timedelta(days=0)
    return ActivityPost.objects.create(
        timestamp=time,
        title=title,
        description=description,
        status=status,
        tags="None")


class ArchivePostTests(TestCase):
    def view_post_test(self):
        """
        Home page should show an empty post list if there is only 1 archive post
        """
        post = create_post("post", "description", 3)
        response = self.client.get("")
        self.assertQuerysetEqual(response.context["latest_posts_list"], [])
        self.assertContains(response, "No posts are available.")


