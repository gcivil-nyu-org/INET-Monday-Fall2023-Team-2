from django.views import generic

from posts.models import ActivityPost

class HomeView(generic.ListView):
    template_name = "symbi/home.html"
    context_object_name = "latest_posts_list"

    def get_queryset(self):
        """Return the last five published posts."""
        return ActivityPost.objects.order_by("-timestamp")[:50]
