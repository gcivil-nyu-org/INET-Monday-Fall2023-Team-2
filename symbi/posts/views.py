from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import ActivityPost


class HomeView(generic.ListView):
    template_name = 'posts/home.html'
    context_object_name = 'latest_posts_list'

    def get_queryset(self):
        """Return the last five published posts."""
        return ActivityPost.objects.order_by('-timestamp')[:5]


class PostDetailsView(generic.DetailView):
    model = ActivityPost
    template_name = 'posts/post_details.html'
    context_object_name = 'post'


class CreatePostView(generic.CreateView):
    model = ActivityPost
    template_name = 'posts/create_post.html'
    fields = ['title', 'description']


def createPost(request):
    title = request.POST.get('title')
    description = request.POST.get('description')
    action = request.POST.get('action')
    if action == 'draft':  # Draft = 1
        new_post = ActivityPost.objects.create(
            title=title, description=description, status=1)
    elif action == 'post':  # Posted = 2
        new_post = ActivityPost.objects.create(
            title=title, description=description, status=2)
    # Handle the newly created post as needed
    return HttpResponseRedirect(reverse('posts:home'))


def deletePost(request, post_id):
    ActivityPost.objects.filter(pk=post_id).delete()
    return HttpResponseRedirect(reverse('posts:home'))

def archivePost(request, post_id):
    currentPost = ActivityPost.objects.filter(pk=post_id)[0]
    currentPost.status = 3
    currentPost.save()
    return HttpResponseRedirect(reverse('posts:home'))

