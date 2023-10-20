from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import ActivityPost

class PostDetailsView(generic.DetailView):
    model = ActivityPost
    template_name = "posts/post_details.html"
    context_object_name = "post"


class CreatePostView(generic.CreateView):
    model = ActivityPost
    template_name = "posts/create_post.html"
    fields = ["title", "description"]


class EditPostView(generic.UpdateView):
    model = ActivityPost
    template_name = "posts/edit_post.html"
    context_object_name = "post"
    fields = ["title", "description"]


def create_post(request):
    title = request.POST.get("title")
    description = request.POST.get("description")
    action = request.POST.get("action")
    if action == "draft":  # Draft = 1
        new_post = ActivityPost.objects.create(
            title=title, description=description, status=1
        )
    elif action == "post":  # Posted = 2
        new_post = ActivityPost.objects.create(
            title=title, description=description, status=2
        )
    # Handle the newly created post as needed
    return HttpResponseRedirect(reverse("home"))


def delete_post(request, post_id):
    ActivityPost.objects.filter(pk=post_id).delete()
    return HttpResponseRedirect(reverse("home"))


def archive_post(request, post_id):
    currentPost = ActivityPost.objects.filter(pk=post_id)[0]
    currentPost.status = 3 # Archived = 3
    currentPost.save()
    return HttpResponseRedirect(reverse("home"))


def edit_post(request, post_id):
    title = request.POST.get("title")
    description = request.POST.get("description")
    action = request.POST.get("action")
    if action == "save":
        post = ActivityPost.objects.get(pk=post_id)
        post.title = title
        post.description = description
        post.save()
    return HttpResponseRedirect(reverse("home"))
