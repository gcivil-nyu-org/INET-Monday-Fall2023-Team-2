from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages

from posts.models import ActivityPost
from .models import SocialUser
from .forms import SignUpForm, LoginForm, ProfileCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required


class LandingPageView(generic.TemplateView):
    template_name = "main/landing_page.html"


class LoginView(generic.View):
    template_name = "main/login.html"
    form_class = LoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, "main/login.html", {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("main:home"))

        return render(request, "main/login.html", {"form": form})


class SignupView(generic.View):
    form_class = SignUpForm
    template_name = "main/signup.html"

    def get(self, request):
        form = self.form_class()
        return render(request, "main/signup.html", {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            profile_data = {
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "full_name": form.cleaned_data["full_name"],
                "password": form.cleaned_data["password1"],
            }

            profile_creation_form = ProfileCreationForm(initial=profile_data)
            return render(
                request, "main/profile_creation.html", {"form": profile_creation_form}
            )

        return render(request, "main/signup.html", {"form": form})


class ProfileCreationView(generic.View):
    template_name = "main/profile_creation.html"

    def post(self, request):
        form_data = ProfileCreationForm(request.POST)

        if form_data.is_valid():
            new_user = SocialUser.objects.create(
                username=form_data.cleaned_data["username"],
                email=form_data.cleaned_data["email"],
                full_name=form_data.cleaned_data["full_name"],
                password=form_data.cleaned_data["password"],
                date_of_birth=form_data.cleaned_data["date_of_birth"],
                major=form_data.cleaned_data["major"],
                pronouns=form_data.cleaned_data["pronouns"],
                tags=form_data.cleaned_data["tags"],
                age=form_data.cleaned_data["age"],
            )

            user = authenticate(
                request,
                username=form_data.cleaned_data["username"],
                password=form_data.cleaned_data["password"],
            )

            if user:
                login(request, user)
                print("Redirecting to home...")
                return redirect("main:home")
            else:
                # Handle authentication failure, if needed
                messages.error(request, "Authentication failed. Please try again.")
        else:
            for field, errors in form_data.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

            return render(request, "main/profile_creation.html", {"form": form_data})


# class ProfileCreationView(generic.FormView):
#     form_class = ProfileCreationForm
#     success_url = reverse_lazy("main:home")
#     template_name = "main/profile_creation.html"
#     initial = {
#         "username": "Test",
#         "full_name": "Profile Test",
#         "email": "fQpZ7@example.com",
#         "password1": "test123",
#         "password2": "test123",
#     }


# def landing(request):
#     template_name = "base.html"
#     # TODO: Check if the user is logged in, if yes, do we directly redirect to the home page?
#     return render(request, template_name)


# @login_required
def home(request):
    template_name = "main/home.html"
    latest_posts_list = ActivityPost.objects.order_by("-timestamp")[:50]
    context = {
        "latest_posts_list": latest_posts_list,
    }
    return render(request, template_name, context)


# def sign_up(request):
#     template_name = "registration/signup.html"
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return HttpResponseRedirect(reverse("main:create_profile"))
#     else:
#         form = SignUpForm()
#     return render(request, template_name, {"form": form})


# class CreateProfileView(generic.CreateView):
#     model = SocialUser
#     form_class = CreateProfileForm
#     template_name = "main/create_profile.html"

#     def get_success_url(self):
#         social_user = SocialUser.objects.get(user=self.request.user)
#         return reverse_lazy("main:profile_view", kwargs={"pk": social_user.pk})

#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.user = self.request.user
#         # self.object.age = self.request.user.age
#         self.object.save()

#         self.user_id = self.object.pk

#         return super(CreateProfileView, self).form_valid(form)


# class ProfileDetailsView(generic.DetailView):
#     model = SocialUser
#     template_name = "main/profile_details.html"
#     context_object_name = "profile"


# # class ProfileCreationView(generic.CreateView):
# #     model = SocialUser
# #     template_name = "main/create_profile.html"
# #     form_class = ProfileCreationForm


# class DiscoverPageView(generic.TemplateView):
#     template_name = "main/discover.html"


# class ProfilePageView(generic.DetailView):
#     model = SocialUser
#     template_name = "main/profile_page.html"
#     context_object_name = "user"


# @login_required
# def delete_account(request):
#     if request.method == "POST":
#         user = SocialUser.objects.get(pk=request.user.pk)

#         if "cancel" in request.POST:
#             return redirect("main:home")
#         else:
#             user.delete()
#             return redirect("login")
#     else:
#         context = {
#             "title": "Delete Account",
#         }
#         return render(request, "main/delete_account.html", context)
