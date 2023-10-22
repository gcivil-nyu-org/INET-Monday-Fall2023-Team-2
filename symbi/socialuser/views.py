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
