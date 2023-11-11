from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import Http404
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
        is_userA = False

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
                        is_userA = False
            else:
                if connection_1:
                    connection_status = connection_1.status
                    is_userA = True

        context["connection_status"] = connection_status
        context["connection_status_choices"] = Connection.ConnectionStatus
        context["viewing_self"] = viewing_self
        context["is_userA"] = is_userA
        return context


@login_required
def notifications(request, pk):
    template_name = "main/notifications.html"
    user_notifications = Notification.objects.filter(recipient_user=request.user)
    notification_types = Notification.NotificationType
    # format the timestamp for display
    time_differences = []
    now = timezone.now()
    for notification in user_notifications:
        time_difference = now - notification.timestamp
        time_difference = format_time_difference(time_difference)
        time_differences.append(time_difference)
    zipped_notifications = zip(user_notifications, time_differences)
    # add context
    context = {
        "zipped_notifications": zipped_notifications,
        "notification_types": notification_types,
    }
    return render(request, template_name, context)


def format_time_difference(time_difference):
    days = time_difference.days
    seconds = time_difference.seconds
    years, remainder = divmod(days, 365)
    months, days = divmod(remainder, 30)
    weeks, days = divmod(days, 7)
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if years > 0:
        return f"{years}y"
    elif months > 0:
        return f"{months}mo"
    elif weeks > 0:
        return f"{weeks}w"
    elif days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "Just now"


@login_required
def connections(request, pk):
    template_name = "main/connections.html"
    viewed_user = get_object_or_404(SocialUser, id=pk)
    viewing_self = request.user == viewed_user
    # someone can only view their own connections
    if not viewing_self:
        return HttpResponseRedirect(reverse("main:profile", kwargs={"pk": pk}))
    else:
        user_connections_1 = Connection.objects.filter(
            userA=request.user, status=Connection.ConnectionStatus.CONNECTED
        )
        user_connections_2 = Connection.objects.filter(
            userB=request.user, status=Connection.ConnectionStatus.CONNECTED
        )
        user_connections = list(user_connections_1) + list(user_connections_2)
        user_connections.sort(key=lambda x: x.timestamp, reverse=True)
        # display the info for the other user, regardless of whether logged in user is userA or userB
        connected_users = []
        for connection in user_connections:
            connected_user = (
                connection.userB
                if connection.userA == request.user
                else connection.userA
            )
            connected_users.append(connected_user)
    return render(request, template_name, {"connected_users": connected_users})


@login_required
def request_connection(request, pk):
    viewed_user = get_object_or_404(SocialUser, pk=pk)
    try:
        # see if connection already exists one way
        connection_1 = Connection.objects.get(
            userA=request.user,
            userB=viewed_user,
        )
    except Connection.DoesNotExist:
        try:
            # see if connection already exists the other way
            connection_2 = Connection.objects.get(
                userA=viewed_user,
                userB=request.user,
            )
        except Connection.DoesNotExist:
            # if neither connection exists, create a new one
            connection = Connection(
                userA=request.user,
                userB=viewed_user,
                status=Connection.ConnectionStatus.REQUESTED_A_TO_B,
            )
            connection.save()
        else:
            if connection_2:
                connection_2.status = Connection.ConnectionStatus.REQUESTED_A_TO_B
                connection_2.save()
    else:
        if connection_1:
            connection_1.status = Connection.ConnectionStatus.REQUESTED_A_TO_B
            connection_1.save()

    # Create a new Notification object for userB
    notification_content = f"{request.user.username} wants to connect."
    notification = Notification(
        recipient_user=connection.userB,
        from_user=request.user,
        content=notification_content,
        type=Notification.NotificationType.CONNECTION_REQUEST,
    )
    notification.save()

    return HttpResponseRedirect(reverse("main:profile", kwargs={"pk": pk}))


@login_required
def cancel_connection_request(request, pk):
    # only userA can cancel a request they made to userB
    userB = get_object_or_404(SocialUser, pk=pk)
    connection = Connection.objects.get(
        userA=request.user,
        userB=userB,
        status=Connection.ConnectionStatus.REQUESTED_A_TO_B,
    )
    if connection:
        connection.delete()
    return HttpResponseRedirect(reverse("main:profile", kwargs={"pk": pk}))


@login_required
def accept_connection(request, pk):
    # from notifications, pk = from_user (userA)
    # only userB can accept a request made from userA
    userA = get_object_or_404(SocialUser, pk=pk)
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
    return HttpResponseRedirect(
        reverse("main:connections", kwargs={"pk": request.user.pk})
    )


@login_required
def remove_connection(request, pk):
    viewed_user = get_object_or_404(SocialUser, pk=pk)
    # regardless of who first requested connection (userA), either user can remove connection
    try:
        connection_1 = Connection.objects.get(
            userA=request.user,
            userB=viewed_user,
            status=Connection.ConnectionStatus.CONNECTED,
        )
    except Connection.DoesNotExist:
        try:
            connection_2 = Connection.objects.get(
                userA=viewed_user,
                userB=request.user,
                status=Connection.ConnectionStatus.CONNECTED,
            )
        except Connection.DoesNotExist:
            raise Http404("Connection not found.")
        else:
            connection_2.delete()
    else:
        connection_1.delete()
    return HttpResponseRedirect(reverse("main:connections", kwargs={"pk": pk}))


class DiscoverPageView(generic.TemplateView):
    template_name = "main/discover.html"
