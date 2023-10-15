from django.urls import path

from . import views

app_name = "posts"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("<int:pk>/", views.PostDetailsView.as_view(), name="post_details"),
    path("create_post/", views.CreatePostView.as_view(), name="create_post"),
    path("create_post_object/", views.create_post, name="create_post_object"),
    path("<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("<int:post_id>/archive/", views.archive_post, name="archive_post"),
    path("edit/<int:pk>/", views.EditPostView.as_view(), name="edit_post"),
    path("edit/", views.edit_post, name="edit_post_object"),
]
