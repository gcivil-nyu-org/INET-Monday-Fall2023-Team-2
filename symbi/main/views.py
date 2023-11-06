from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from posts.models import ActivityPost
from .forms import SignUpForm
from django.contrib import messages


def home(request):
    template_name = "main/home.html"
    latest_posts_list = ActivityPost.objects.order_by("-timestamp")[:50]
    print(latest_posts_list)
    context = {
        "latest_posts_list": latest_posts_list,
    }
    return render(request, template_name, context)


def login(request, user):
    context = {}
    return render(request, "registration/login.html", context)


def sign_up(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = create_user(request, form)
            login(request, user)
            messages.success(request, "User created successfully.")
            return redirect("/")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


def create_user(request, form):
    if request.method == "POST":
        user = form.save(commit=False)
        user.username = form.cleaned_data["username"]
        user.email = form.cleaned_data["email"]
        user.date_of_birth = form.cleaned_data["date_of_birth"]
        user.set_password(form.cleaned_data["password1"])
        user.save()
        return HttpResponseRedirect("create_profile")
    else:
        form = SignUpForm()
        return render(request, "registration/signup.html", {"form": form})
