from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404

from main.models import SocialUser
from .models import ActivityPost, Comment
from .forms import NewPostForm, EditPostForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin


@method_decorator(login_required, name="dispatch")
class CreatePostView(LoginRequiredMixin, generic.CreateView):
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
            self.object.status = ActivityPost.PostStatus.DRAFT
        elif action == "post":
            self.object.status = ActivityPost.PostStatus.ACTIVE

        self.object.save()

        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class EditPostView(LoginRequiredMixin, generic.UpdateView):
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


@method_decorator(login_required, name="dispatch")
class PostDetailsView(LoginRequiredMixin, generic.DetailView):
    model = ActivityPost
    template_name = "posts/post_details.html"
    context_object_name = "post"

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(
            ActivityPost,
            poster__username=self.kwargs["poster"],
            pk=self.kwargs["pk"],
        )
        if (
            post.status == ActivityPost.PostStatus.DRAFT
            or post.status == ActivityPost.PostStatus.ARCHIVED
        ) and post.poster != request.user:
            return HttpResponseRedirect(reverse("main:home"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(post=self.object).order_by(
            "-timestamp"
        )
        return context

    def post(self, request, *args, **kwargs):
        new_comment = self.request.POST.get("new_comment")
        if new_comment:
            poster = SocialUser(username=self.kwargs["poster"])
            post = ActivityPost(poster=poster, pk=self.kwargs["pk"])
            taggedUsername = [
                word[1:] for word in new_comment.split() if word.startswith("@")
            ]
            print("Tagged Username = ", taggedUsername)
            taggedUsers = SocialUser.objects.filter(username__in=taggedUsername)
            print("Tagged User = ", taggedUsers)
            comment = Comment.objects.create(
                commentPoster=request.user,
                post=post,
                text=new_comment,
                timestamp=timezone.now(),
            )
            comment.taggedUsers.set(taggedUsers)

        return redirect(
            reverse_lazy(
                "posts:post_details",
                kwargs={
                    "poster": poster.username,
                    "pk": post.id,
                },
            )
        )


@method_decorator(login_required, name="dispatch")
class ArchivePostView(LoginRequiredMixin, generic.RedirectView):
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(
            ActivityPost,
            poster__username=self.kwargs["poster"],
            pk=self.kwargs["pk"],
        )
        post.status = ActivityPost.PostStatus.ARCHIVED
        post.save()
        return redirect(
            reverse_lazy(
                "main:profile_page", kwargs={"username": self.request.user.username}
            )
        )


@method_decorator(login_required, name="dispatch")
class DeleteCommentView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        poster = SocialUser.objects.filter(username=self.kwargs["post_poster"]).first()
        post = ActivityPost(poster=poster, pk=self.kwargs["post_id"])
        comment = Comment.objects.get(
            commentPoster__username=self.kwargs["comment_poster"],
            pk=self.kwargs["comment_id"],
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


# def edit_comment(request, pk, comment_id):
#     post = ActivityPost.objects.filter(pk=pk)[0]
#     comment = Comment.objects.filter(pk=comment_id, post=post)[0]

#     if request.method == "POST":
#         current_user = request.user
#         comment_user = comment.user
#         if current_user.id == comment_user.id:
#             edited_comment = request.POST.get("text")
#             comment.text = edited_comment
#             comment.save()
#             return HttpResponseRedirect(reverse("posts:post_details_view", args=[pk]))

#     return HttpResponseRedirect(reverse("posts:post_details_view", args=[pk]))


@method_decorator(login_required, name="dispatch")
class EditCommentView(LoginRequiredMixin, generic.UpdateView):
    model = Comment
    template_name = "posts/edit_comment.html"
    context_object_name = "edited_comment"
    fields = ["text"]

    def get_object(self, queryset=None):
        post_poster = SocialUser.objects.filter(
            username=self.kwargs["post_poster"]
        ).first()
        comment_poster = SocialUser.objects.filter(
            username=self.kwargs["comment_poster"]
        ).first()
        self.post = ActivityPost(poster=post_poster, pk=self.kwargs["post_id"])
        comment = Comment.objects.get(
            commentPoster=comment_poster,
            pk=self.kwargs["comment_id"],
        )
        return comment

    def form_valid(self, form):
        current_user = self.request.user
        comment_user = self.object.commentPoster
        if current_user == comment_user:
            edited_comment = form.cleaned_data["text"]
            self.object.text = edited_comment
            self.object.save()

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "posts:post_details",
            kwargs={
                "poster": self.post.poster.username,
                "pk": self.post.id,
            },
        )

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["user"] = self.request.user
    #     context["commentPoster"] = self.object.commentPoster
    #     return context

    # def form_valid(self, form):
    #     print("Current user:", self.request.user)
    #     print(
    #         "Comment author:", form.instance.commentPoster
    #     )  # Adjust based on your field name
    #     return super().form_valid(form)

    # def get_queryset(self):
    #     # Ensure that only the comments of the current user are editable
    #     return Comment.objects.filter(commentPoster=self.request.user)

    # def get_success_url(self):
    #     return reverse_lazy(
    #         "posts:post_details_view", kwargs={"pk": self.object.post.pk}
    #     )


# OLD FUNCTIONS **************************************************
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


# @login_required
# def add_comment(request, post_id):
#     if request.method == "POST":
#         text = request.POST.get("comment", None)
#         if text:
#             post = ActivityPost.objects.get(pk=post_id)
#             taggedUsername = [word[1:] for word in text.split() if word.startswith('@')]
#             taggedUsers = SocialUser.objects.filter(username__in=taggedUsername)
#             comment = Comment.objects.create(
#                 commentPoster=request.user,
#                 post=post,
#                 text=text,
#                 timestamp=timezone.now(),
#             )
#     return HttpResponseRedirect(reverse("posts:post_details_view", args=[post_id]))


# def edit_comment(request, pk, comment_id):
#     post = ActivityPost.objects.filter(pk=pk)[0]
#     comment = Comment.objects.filter(pk=comment_id, post=post)[0]

#     if request.method == "POST":
#         current_user = request.user
#         comment_user = comment.user
#         if current_user.id == comment_user.id:
#             edited_comment = request.POST.get("text")
#             comment.text = edited_comment
#             comment.save()
#             return HttpResponseRedirect(reverse("posts:post_details_view", args=[pk]))

#     return HttpResponseRedirect(reverse("posts:post_details_view", args=[pk]))


@login_required
def delete_comment(request, post_id, comment_id):
    current_comment = Comment.objects.get(pk=comment_id)
    current_user = request.user
    if current_comment.commentPoster_id == current_user.id:
        current_comment.delete()
    return HttpResponseRedirect(reverse("posts:post_details_view", args=[post_id]))
