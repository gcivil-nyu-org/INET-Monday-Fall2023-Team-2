from django.urls import reverse_lazy
from django.views import generic

from .models import SocialUser
from .forms import SocialUserForm


class CreateProfileView(generic.CreateView):
    model = SocialUser
    form_class = SocialUserForm
    template_name = "socialuser/create_profile.html"
    redirect_to = "socialuser:profile_details"

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
