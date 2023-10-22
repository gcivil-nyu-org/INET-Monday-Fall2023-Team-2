from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render

from .models import InterestTag, SocialUser
from .forms import SocialUserForm


class CreateProfileView(generic.CreateView):
    model = SocialUser
    form_class = SocialUserForm
    template_name = "socialuser/create_profile.html"

    def get_success_url(self):
        return reverse_lazy(
            "socialuser:profile_view",
            kwargs={
                "pk": self.user_id,
            },
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        self.user_id = self.object.pk

        return super(CreateProfileView, self).form_valid(form)


class ProfileDetailsView(generic.DetailView):
    model = SocialUser
    template_name = "socialuser/profile_details.html"
    context_object_name = "profile"


# def create_profile(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         age = request.POST.get("age")
#         major = request.POST.get("major")
#         pronouns = request.POST.get("pronouns")
#         tags = request.POST.get("tags")

#         new_profile = SocialUser.objects.create(
#             name=name, age=age, major=major, pronouns=pronouns, tags=tags
#         )

#     interest_tags = InterestTag.objects.all()

#     return render(request, "create_profile.html", {"interest_tags": interest_tags})
