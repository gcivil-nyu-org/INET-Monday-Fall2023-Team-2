from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from posts.models import ActivityPost
from .models import SocialUser, Connection
from .forms import SignUpForm


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewed_user = self.get_object()
        viewing_self = self.request.user == viewed_user
        connection_status = Connection.ConnectionStatus.NOT_CONNECTED

        if self.request.user.is_authenticated and not viewing_self:
            try:
                connection_1 = Connection.objects.get(
                    userA=self.request.user, userB=viewed_user
                )
                connection_2 = Connection.objects.get(
                    userA=viewed_user, userB=self.request.user
                )
                if (
                    connection_1.status == Connection.ConnectionStatus.CONNECTED
                    or connection_2.status == Connection.ConnectionStatus.CONNECTED
                ):
                    connection_status = Connection.ConnectionStatus.CONNECTED
                elif (
                    connection_1.status == Connection.ConnectionStatus.REQUESTED_A_TO_B
                    or connection_2.status
                    == Connection.ConnectionStatus.REQUESTED_A_TO_B
                ):
                    connection_status = Connection.ConnectionStatus.REQUESTED_A_TO_B
            except Connection.DoesNotExist:
                connection_status = Connection.ConnectionStatus.NOT_CONNECTED

        context["connection_status"] = connection_status
        context["connection_status_choices"] = Connection.ConnectionStatus
        context["viewing_self"] = viewing_self
        return context


@login_required
def request_connection(request, pk):
    viewed_user = get_object_or_404(SocialUser, pk=pk)
    connection = Connection(
        userA=request.user,
        userB=viewed_user,
        status=Connection.ConnectionStatus.REQUESTED_A_TO_B,
    )
    connection.save()
    return HttpResponseRedirect(reverse("main:profile", args=[pk]))


@login_required
def accept_connection(request, userA_pk):
    userA = get_object_or_404(SocialUser, pk=userA_pk)
    connection = get_object_or_404(
        Connection,
        userA=userA,
        userB=request.user,
        status=Connection.ConnectionStatus.REQUESTED_A_TO_B,
    )
    if connection:
        connection.status = Connection.ConnectionStatus.CONNECTED
        connection.timestamp = timezone.now()
        connection.save()
    return HttpResponseRedirect(reverse("main:home"))


@login_required
def remove_connection(request, pk):
    viewed_user = get_object_or_404(SocialUser, pk=pk)
    # regardless of who first requested connection (userA), either user can remove connection
    connection_1 = Connection.objects.filter(
        userA=request.user,
        userB=viewed_user,
        status=Connection.ConnectionStatus.CONNECTED,
    ).first()
    connection_2 = Connection.objects.filter(
        userA=viewed_user,
        userB=request.user,
        status=Connection.ConnectionStatus.CONNECTED,
    ).first()
    if connection_1:
        connection_1.delete()
    elif connection_2:
        connection_2.delete()
    return HttpResponseRedirect(reverse("main:profile", args=[pk]))
