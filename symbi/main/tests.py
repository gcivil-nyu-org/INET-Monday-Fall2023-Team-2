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
            username='testuser',
            password='testpassword'
        )

    def test_home_page_view(self):
        # Test that the home page returns a 200 status code for an authenticated user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('main:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')

    def test_login_view(self):
        # Test that the login view returns a 200 status code
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/login.html')

        # Test a successful login
        response = self.client.post(reverse('main:login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)  # 302 is the HTTP status code for a redirect
        self.assertRedirects(response, reverse('main:home'))

    def test_signup_view(self):
        # Test that the signup view returns a 200 status code
        response = self.client.get(reverse('main:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/signup.html')

        # Test a successful signup
        response = self.client.post(reverse('main:signup'), {
            'username': 'newuser',
            'email': 'newuser@nyu.edu',
            'password1': 'newpassword',
            'password2': 'newpassword',
            # Add other required fields for signup
        })
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        # Test that the logout view logs out the user and redirects to the landing page
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('main:logout'))
        self.assertEqual(response.status_code, 302)  # 302 is the HTTP status code for a redirect
        self.assertRedirects(response, reverse('main:landing'))
        # You may also want to test cases where logout fails

    def test_profile_page_view(self):
        # Test that the profile page view returns a 200 status code for an authenticated user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('main:profile_page', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/profile_page.html')

    def test_edit_profile_view(self):
        # Test that the edit profile view returns a 200 status code for an authenticated user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('main:edit_profile_page', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/edit_profile_page.html')

        # Test a successful profile edit
        response = self.client.post(reverse('main:edit_profile_page', kwargs={'username': 'testuser'}), {
            # Add fields to update
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(reverse('main:profile_page', kwargs={'username': 'testuser'}), response.url)

        # You may also want to test cases where profile edit fails

    def tearDown(self):
        # Clean up after the tests if needed
        pass


