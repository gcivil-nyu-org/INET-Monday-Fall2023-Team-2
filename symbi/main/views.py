from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth import login

from posts.models import ActivityPost
from .models import SocialUser
from .forms import SignUpForm, CreateProfileForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required


# @login_required
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
            return HttpResponseRedirect(reverse("main:create_profile"))
    else:
        form = SignUpForm()
    return render(request, template_name, {"form": form})


class CreateProfileView(generic.CreateView):
    model = SocialUser
    form_class = CreateProfileForm
    template_name = "main/create_profile.html"

    def get_success_url(self):
        social_user = SocialUser.objects.get(user=self.request.user)
        return reverse_lazy("main:profile_view", kwargs={"pk": social_user.pk})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        # self.object.age = self.request.user.age
        self.object.save()

        self.user_id = self.object.pk

        return super(CreateProfileView, self).form_valid(form)


class ProfileDetailsView(generic.DetailView):
    model = SocialUser
    template_name = "main/profile_details.html"
    context_object_name = "profile"


@login_required
def delete_account(request):
    if request.method == "POST":
        user = SocialUser.objects.get(pk=request.user.pk)

        if "cancel" in request.POST:
            return redirect("main:home")
        else:
            user.delete()
            login(request, None)
            return redirect("/login")
    else:
        context = {
            "title": "Delete Account",
        }
        return render(request, "main/delete_account.html", context)
