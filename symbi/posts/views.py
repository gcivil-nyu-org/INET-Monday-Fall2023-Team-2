from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import ActivityPost, Comment


class PostDetailsView(generic.DetailView):
    model = ActivityPost
    template_name = "posts/post_details.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context["post"]
        comments = Comment.objects.filter(post=post).order_by("-timestamp")
        context[("comments")] = comments
        return context


class CreatePostView(generic.CreateView):
    model = ActivityPost
    template_name = "posts/create_post.html"
    fields = ["title", "description"]


class EditPostView(generic.UpdateView):
    model = ActivityPost
    template_name = "posts/edit_post.html"
    context_object_name = "post"
    fields = ["title", "description"]


# class EditCommentView(generic.UpdateView):
#     model = Comment
#     template_name = "posts/edit_comment.html"
#     context_object_name = "edited_comment"
#     fields = ["text"]


def create_post(request):
    title = request.POST.get("title")
    description = request.POST.get("description")
    action = request.POST.get("action")
    if action == "draft":  # Draft = 1
        _ = ActivityPost.objects.create(title=title, description=description, status=1)
    elif action == "post":  # Posted = 2
        _ = ActivityPost.objects.create(title=title, description=description, status=2)
    # Handle the newly created post as needed
    return HttpResponseRedirect(reverse("main:home"))


def delete_post(request, post_id):
    ActivityPost.objects.filter(pk=post_id).delete()
    return HttpResponseRedirect(reverse("main:home"))


def archive_post(request, post_id):
    currentPost = ActivityPost.objects.filter(pk=post_id)[0]
    currentPost.status = 3  # Archived = 3
    currentPost.save()
    return HttpResponseRedirect(reverse("main:home"))


def edit_post(request, post_id):
    title = request.POST.get("title")
    description = request.POST.get("description")
    action = request.POST.get("action")
    if action == "save":
        post = ActivityPost.objects.get(pk=post_id)
        post.title = title
        post.description = description
        post.save()
    return HttpResponseRedirect(reverse("main:home"))


def add_comment(request, post_id):
    if request.method == "POST":
        text = request.POST.get("comment", None)
        if text:
            post = ActivityPost.objects.get(pk=post_id)
            Comment.objects.create(
                commentPoster=request.user,
                post=post,
                text=text,
                timestamp=timezone.now(),
            )
    return HttpResponseRedirect(reverse("posts:post_details_view", args=[post_id]))


# def edit_comment(request, post_id, comment_id):
#     comment = Comment.objects.filter(pk=comment_id)
#
#     if request.method == 'POST':
#         print("form submitted")
#         new_text = request.POST.get('edited_comment', '')
#         comment.text = new_text
#         comment.save()
#         return HttpResponseRedirect(reverse('posts:post_details_view', args=[post_id]))
#
#     return HttpResponseRedirect(reverse('posts:post_details_view', args=[post_id]))


def delete_comment(request, post_id, comment_id):
    comment = Comment.objects.filter(pk=comment_id)
    comment.delete()
    return HttpResponseRedirect(reverse("posts:post_details_view", args=[post_id]))
