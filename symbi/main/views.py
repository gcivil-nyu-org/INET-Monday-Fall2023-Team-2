from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from posts.models import ActivityPost
from .models import SocialUser, Connection, Notification
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
            except Connection.DoesNotExist:
                try:
                    connection_2 = Connection.objects.get(
                        userA=viewed_user, userB=self.request.user
                    )
                except Connection.DoesNotExist:
                    print("Debug: CONNECTION DOES NOT EXIST")
                    connection_status = Connection.ConnectionStatus.NOT_CONNECTED
                else:
                    if connection_2:
                        connection_status = connection_2.status
            else:
                if connection_1:
                    connection_status = connection_1.status

        context["connection_status"] = connection_status
        context["connection_status_choices"] = Connection.ConnectionStatus
        context["viewing_self"] = viewing_self
        return context


@login_required
def notifications(request, pk):
    template_name = "main/notifications.html"
    user_notifications = Notification.objects.filter(user=request.user)
    return render(request, template_name, {"notifications": user_notifications})


@login_required
def connections(request, pk):
    template_name = "main/connections.html"
    # viewed_user = get_object_or_404(SocialUser, id=pk)
    # viewing_self = request.user == viewed_user
    # someone can only view their own connections
    # if not viewing_self:
    # return HttpResponseRedirect(reverse("main:profile", args=[pk]))
    # else:
    user_connections_1 = Connection.objects.filter(
        userA=request.user, status=Connection.ConnectionStatus.CONNECTED
    )
    user_connections_2 = Connection.objects.filter(
        userB=request.user, status=Connection.ConnectionStatus.CONNECTED
    )
    user_connections = list(user_connections_1) + list(user_connections_2)
    user_connections.sort(key=lambda x: x.timestamp, reverse=True)
    return render(request, template_name, {"connections": user_connections})


@login_required
def request_connection(request, pk):
    viewed_user = get_object_or_404(SocialUser, pk=pk)
    connection = Connection(
        userA=request.user,
        userB=viewed_user,
        status=Connection.ConnectionStatus.REQUESTED_A_TO_B,
    )
    connection.save()

    # Create a new Notification object for userB
    notification_content = f"{request.user.username} wants to connect"
    notification = Notification(
        user=connection.userB,
        content=notification_content,
        type=Notification.NotificationType.CONNECTION_REQUEST,
    )
    notification.save()

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
    return HttpResponseRedirect(reverse("main:connections", args=[pk]))


class DiscoverPageView(generic.TemplateView):
    template_name = "main/discover.html"
