from django.urls import path

from . import views

app_name = 'posts'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('<int:pk>/', views.PostDetailsView.as_view(), name='post_details'),
    path('create_post/', views.CreatePostView.as_view(), name='create_post'),
    path('createPost/', views.createPost, name='createPost'),
    path('<int:post_id>/delete/', views.deletePost, name='deletePost'),
    path('edit/<int:pk>/', views.EditPostView.as_view(), name='edit_post'),
    path('edit/', views.edit_post, name='editPost'),
]