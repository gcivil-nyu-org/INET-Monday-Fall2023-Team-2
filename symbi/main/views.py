from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render
from django.contrib.auth import login

from posts.models import ActivityPost
from .models import SocialUser
from .forms import SignUpForm, ProfileCreationForm


def home(request):
    template_name = "main/home.html"
    latest_posts_list = ActivityPost.objects.order_by("-timestamp")[:50]
    context = {
        "latest_posts_list": latest_posts_list,
    }
    return render(request, template_name, context)


def sign_up(request):
    template_name = "registration/signup.html"
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("main:home"))
    else:
        form = SignUpForm()
    return render(request, template_name, {"form": form})


class ProfileDetailsView(generic.DetailView):
    model = SocialUser
    template_name = "main/profile_details.html"
    context_object_name = "profile"


class ProfileCreationView(generic.CreateView):
    model = SocialUser
    template_name = "main/create_profile.html"
    form_class = ProfileCreationForm


class DiscoverPageView(generic.TemplateView):
    template_name = "main/discover.html"
