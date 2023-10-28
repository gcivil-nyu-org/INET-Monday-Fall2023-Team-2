from django.test import TestCase
from django.utils import timezone
from symbi.posts.models import ActivityPost
from symbi.socialuser.models import SocialUser, InterestTag
import datetime

# Create your tests here.
def create_post_user(title, description, status):
    # Status values:
    # 1: Draft
    # 2: Posted
    # 3: Archived
    time = timezone.now() + datetime.timedelta(days=days)
    tag = InterestTag.objects.create(name = "None")
    socialuser = SocialUser.objects.create(user_id="1", name="Louis", age=57, major="CS", pronouns=2, tags=tag)
    post = ActivityPost.objects.create(socialuser=socialuser, timestamp=time, title=title, description=description, status=status, tags=tag)
    return post, socialuser

class ProfileArchiveTest(TestCase):
    def view_archive_post_test(self):
        post, user = create_post_user("post", "Desc", 3)
        response = self.client.get(reverse("symbi::profile/Louis"))

        self.assertQuertSetEqual(
            response.context["post"], post
        )





#
# class ArchivePostTests(TestCase):
#     def archive_post_test(self):
#         post = create_post("post", "description", 2)
#         post.get("")
#         return