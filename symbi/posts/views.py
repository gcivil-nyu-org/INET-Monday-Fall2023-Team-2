from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import ActivityPost
from django.contrib.auth.decorators import login_required


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


@login_required
def create_post(request):
    title = request.POST.get("title")
    description = request.POST.get("description")
    action = request.POST.get("action")
    if action == "draft":  # Draft = 1
        _ = ActivityPost.objects.create(
            title=title, description=description, status=1, poster_id=request.user.id
        )
    elif action == "post":  # Posted = 2
        _ = ActivityPost.objects.create(
            title=title, description=description, status=2, poster_id=request.user.id
        )
    # Handle the newly created post as needed
    return HttpResponseRedirect(reverse("main:home"))


@login_required
def archive_post(request, post_id):
    current_post = ActivityPost.objects.get(pk=post_id)
    current_user = request.user

    if current_post.poster_id == current_user.id:
        current_post.status = 3  # Archived = 3
        current_post.save()
        return HttpResponseRedirect(reverse("main:home"))
    else:
        pass


@login_required
def delete_post(request, post_id):
    current_post = ActivityPost.objects.get(pk=post_id)
    current_user = request.user

    if current_post.poster_id == current_user.id:
        current_post.delete()
        return HttpResponseRedirect(reverse("main:home"))
    else:
        pass


@login_required
def edit_post(request, post_id):
    title = request.POST.get("title")
    description = request.POST.get("description")
    action = request.POST.get("action")

    if action == "save":
        current_post = ActivityPost.objects.get(pk=post_id)
        current_user = request.user

        if current_post.poster_id == current_user.id:
            current_post.title = title
            current_post.description = description
            current_post.save()
            return HttpResponseRedirect(reverse("main:home"))
        else:
            pass

    elif action == "post":
        current_post = ActivityPost.objects.get(pk=post_id)
        current_user = request.user

        if current_post.poster_id == current_user.id:
            current_post.title = title
            current_post.description = description
            current_post.status = ActivityPost.PostStatus.ACTIVE
            current_post.save()
            return HttpResponseRedirect(reverse("main:home"))
        else:
            pass

    else:
        pass
