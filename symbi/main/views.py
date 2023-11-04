from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from posts.models import ActivityPost
from .forms import SignUpForm


def home(request):
    template_name = "main/home.html"
    latest_posts_list = ActivityPost.objects.order_by("-timestamp")[:50]
    context = {
        "latest_posts_list": latest_posts_list,
    }
    return render(request, template_name, context)


def login(request, user):
    context = {}
    return render(request, "login/login.html", context)


# def sign_up(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return HttpResponseRedirect(reverse("main:home"))
#     else:
#         form = SignUpForm()
#     return render(request, 'registration/signup.html', {'form': form})

# def signup_and_create_user(request):
#   if request.method == 'POST':
#     form = SignUpForm(request.POST)
#     if form.is_valid():
#       user = form.save(commit=False)
#       user.username = form.cleaned_data['username']
#       user.email = form.cleaned_data['email']
#       user.date_of_birth=form.cleaned_data['date_of_birth']
#       user.set_password(form.cleaned_data['password'])
#       user.save()
#       login(request, user)
#       return HttpResponseRedirect(reverse("main:home"))
#   else:
#     form = SignUpForm()
#   return render(request, 'registration/signup.html', {'form': form})

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = create_user(request, form)
            login(request, user)
            return HttpResponseRedirect(reverse("main:home"))
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def create_user(request, form):
    if request.method == 'POST':
        user = form.save(commit=False)
        user.username = form.cleaned_data['username']
        user.email = form.cleaned_data['email']
        user.date_of_birth = form.cleaned_data['date_of_birth']
        user.set_password(form.cleaned_data['password1'])
        user.save()
        return HttpResponseRedirect('create_profile')
    else:
        form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})
