from django.urls import path

from . import views

app_name = "posts"
urlpatterns = [
    path("new/", views.CreatePostView.as_view(), name="create_post"),
    path(
        "post/<slug:poster>/<int:pk>/",
        views.PostDetailsView.as_view(),
        name="post_details",
    ),
    path(
        "post/<slug:poster>/<int:pk>/edit/",
        views.EditPostView.as_view(),
        name="edit_post",
    ),
    path(
        "post/<slug:post_poster>/<int:post_id>/comment/delete/<slug:comment_poster>/<int:comment_id>/",
        views.DeleteCommentView.as_view(),
        name="delete_comment",
    ),
    path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path(
        "post/<slug:post_poster>/<int:post_id>/comment/edit/<slug:comment_poster>/<int:comment_id>/",
        views.EditCommentView.as_view(),
        name="edit_comment",
    ),
    path(
        "<int:post_id>/archive_request/",
        views.archive_post,
        name="archive_post_request",
    ),
    path(
        "post/<slug:poster>/<int:pk>/archive/",
        views.ArchivePostView.as_view(),
        name="archive_post",
    ),
    # path(
    #     "post/<slug:poster>/<int:pk>/edit_comment_request/<int:comment_id>/",
    #     views.edit_comment,
    #     name="edit_comment_request",
    # ),
    path(
        "<int:post_id>/edit_comment/<int:pk>/",
        views.EditCommentView.as_view(),
        name="edit_comment",
    ),
    path(
        "<int:post_id>/delete_comment/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),
]
