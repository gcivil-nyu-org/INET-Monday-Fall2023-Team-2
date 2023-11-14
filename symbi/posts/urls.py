from django.urls import path

from . import views

app_name = "posts"
urlpatterns = [
    path("<int:pk>/", views.PostDetailsView.as_view(), name="post_details_view"),
    path("create/", views.CreatePostView.as_view(), name="create_post_view"),
    path("create_request/", views.create_post, name="create_post_request"),
    path(
        "<int:post_id>/delete_request/", views.delete_post, name="delete_post_request"
    ),
    path(
        "<int:post_id>/archive_request/",
        views.archive_post,
        name="archive_post_request",
    ),
    path("<int:pk>/edit/", views.EditPostView.as_view(), name="edit_post_view"),
    path("<int:post_id>/edit_request/", views.edit_post, name="edit_post_request"),
    path("<int:post_id>/add_comment/", views.add_comment, name="add_comment"),
    # path("<int:pk>/edit_comment_request/<int:comment_id>/", views.edit_comment, name="edit_comment_request"),
    # path("<int:pk>/edit_comment/<int:comment_id>/", views.EditCommentView.as_view(), name="edit_comment"),
    path(
        "<int:post_id>/delete_comment/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),
]
