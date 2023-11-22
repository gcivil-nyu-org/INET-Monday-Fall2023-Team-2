from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404

from main.models import SocialUser
from .models import ActivityPost, Comment
from .forms import NewPostForm, EditPostForm
from django.contrib.auth.decorators import login_required


class CreatePostView(generic.CreateView):
    model = ActivityPost
    template_name = "posts/create_post.html"
    form_class = NewPostForm

    def get_success_url(self):
        return reverse_lazy(
            "posts:post_details",
            kwargs={
                "poster": self.object.poster.username,
                "pk": self.object.id,
            },
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.poster = self.request.user

        action = self.request.POST.get("action")
        if action == "draft":
            self.object.status = ActivityPost.DRAFT
        elif action == "post":
            self.object.status = ActivityPost.PostStatus.ACTIVE

        self.object.save()

        return super().form_valid(form)


class EditPostView(generic.UpdateView):
    model = ActivityPost
    template_name = "posts/edit_post.html"
    form_class = EditPostForm

    def get_success_url(self):
        post = get_object_or_404(
            ActivityPost,
            poster__username=self.kwargs["poster"],
            pk=self.kwargs["pk"],
        )
        return reverse_lazy(
            "posts:post_details",
            kwargs={
                "poster": post.poster.username,
                "pk": post.id,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = get_object_or_404(
            ActivityPost,
            poster__username=self.kwargs["poster"],
            pk=self.kwargs["pk"],
        )
        return context

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(
            ActivityPost,
            poster__username=self.kwargs["poster"],
            pk=self.kwargs["pk"],
        )
        post.title = request.POST.get("title")
        post.description = request.POST.get("description")
        post.tags.set(request.POST.getlist("tags"))
        post.save()
        return redirect(self.get_success_url())


class PostDetailsView(generic.DetailView):
    model = ActivityPost
    template_name = "posts/post_details.html"
    context_object_name = "post"
    slug_field = "title"
    slug_url_kwarg = "title"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(post=self.object).order_by(
            "-timestamp"
        )
        return context

    def post(self, request, *args, **kwargs):
        new_comment = self.request.POST.get("new_comment")
        poster = SocialUser(username=self.kwargs["poster"])
        post = ActivityPost(poster=poster, pk=self.kwargs["pk"])
        Comment.objects.create(
            commentPoster=request.user,
            post=post,
            text=new_comment,
            timestamp=timezone.now(),
        )
        return redirect(
            reverse_lazy(
                "posts:post_details",
                kwargs={
                    "poster": poster.username,
                    "pk": post.id,
                },
            )
        )


class DeleteCommentView(generic.View):
    def get(self, request, *args, **kwargs):
        poster = SocialUser.objects.filter(username=self.kwargs["post_poster"]).first()
        post = ActivityPost(poster=poster, pk=self.kwargs["post_pk"])
        comment = Comment.objects.get(
            commentPoster__username=self.kwargs["comment_poster"],
            pk=self.kwargs["comment_pk"],
        )
        comment.delete()
        return redirect(
            reverse_lazy(
                "posts:post_details",
                kwargs={
                    "poster": post.poster.username,
                    "pk": post.id,
                },
            )
        )


class EditCommentView(generic.View):
    def post(self, request, *args, **kwargs):
        post = ActivityPost(
            poster__username=self.kwargs["post_poster"],
            pk=self.kwargs["post_pk"],
        )
        comment = Comment.objects.get(
            commentPoster__username=self.kwargs["comment_poster"],
            pk=self.kwargs["comment_pk"],
        )
        edited_comment = request.POST.get("edited_comment")
        comment.content = edited_comment
        comment.save()
        return redirect(
            reverse_lazy(
                "posts:post_details",
                kwargs={
                    "poster": post.poster.username,
                    "pk": post.id,
                },
            )
        )


# class EditCommentView(generic.UpdateView):
#     model = Comment
#     template_name = "posts/edit_comment.html"
#     context_object_name = "edited_comment"
#     fields = ["text"]


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
def delete_post(request, post_id):
    current_post = ActivityPost.objects.get(pk=post_id)
    current_user = request.user

    if current_post.poster_id == current_user.id:
        current_post.delete()
        return HttpResponseRedirect(reverse("main:home"))
    else:
        pass


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


@login_required
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


@login_required
def delete_comment(request, post_id, comment_id):
    current_comment = Comment.objects.get(pk=comment_id)
    current_user = request.user
    if current_comment.commentPoster_id == current_user.id:
        current_comment.delete()
    return HttpResponseRedirect(reverse("posts:post_details_view", args=[post_id]))
