from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import ActivityPost, ActivityTag, Comment

class HomeView(generic.ListView):
    template_name = 'posts/home.html'
    context_object_name = 'latest_posts_list'

    def get_queryset(self):
        """Return the last five published posts."""
        return ActivityPost.objects.order_by('-timestamp')[:5]
