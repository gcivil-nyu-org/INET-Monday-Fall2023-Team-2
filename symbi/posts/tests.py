from django.test import TestCase
from django.utils import timezone
from .models import ActivityPOst
import datedate

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
        status=status)


class TestHomePage(TestCase):
    def test_no_post(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts are available.")
        self.assertQuerysetEqual(response.context["latest_posts_list"], [])





