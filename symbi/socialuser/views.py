from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import SocialUser

class ProfileView(generic.DetailView):
    model = SocialUser
    template_name = "posts/profile.html"
    context_object_name = "socialuser"
