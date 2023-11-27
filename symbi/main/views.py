from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from posts.models import ActivityPost
from .models import SocialUser, Connection, Notification, InterestTag
from .forms import SignupForm, LoginForm, SearchForm, EditProfileForm


class LandingPageView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy("main:home"))
        else:
            return render(request, template_name="main/landing.html")


class LoginView(LoginView):
    template_name = "main/login.html"
    authentication_form = LoginForm
    success_url = reverse_lazy("main:home")


class SignupView(generic.FormView):
    template_name = "main/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("main:home")

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect(self.success_url)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

            return render(request, "main/signup.html", {"form": form})


class LogoutView(generic.RedirectView):
    url = reverse_lazy("main:landing")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return super().get(request, *args, **kwargs)


class HomePageView(LoginRequiredMixin, generic.ListView):
    model = ActivityPost
    template_name = "main/home.html"
    redirect_field_name = "main:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get posts where the users interests is in the posts tags
        context["interests_posts"] = ActivityPost.objects.filter(
            tags__in=self.request.user.tags.all(),
            status=ActivityPost.PostStatus.ACTIVE,
        )
        user_connections = Connection.get_active_connections(self.request.user)
        connected_users = [
            connection.receiver
            if connection.receiver != self.request.user
            else connection.requester
            for connection in user_connections
        ]
        # Get posts where the users connections is in the posts poster
        context["connection_posts"] = ActivityPost.objects.filter(
            poster__in=connected_users,
            status=ActivityPost.PostStatus.ACTIVE,
        )
        return context


class ProfilePageView(LoginRequiredMixin, generic.DetailView):
    model = SocialUser
    template_name = "main/profile_page.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return get_object_or_404(SocialUser, username=self.kwargs["username"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_posts"] = ActivityPost.objects.filter(
            poster=self.object, status=ActivityPost.PostStatus.ACTIVE
        )
        context["drafted_posts"] = ActivityPost.objects.filter(
            poster=self.object, status=ActivityPost.PostStatus.DRAFT
        )
        context["archived_posts"] = ActivityPost.objects.filter(
            poster=self.object, status=ActivityPost.PostStatus.ARCHIVED
        )
        context["connection"] = Connection.get_connection(
            self.request.user, self.object
        )
        return context


class EditProfileView(LoginRequiredMixin, generic.UpdateView):
    model = SocialUser
    form_class = EditProfileForm
    template_name = "main/edit_profile_page.html"
    context_object_name = "profile"

    def get_success_url(self):
        return reverse_lazy(
            "main:profile_page", kwargs={"username": self.request.user.username}
        )

    def get_initial(self):
        initial = super().get_initial()
        initial["username"] = self.request.user.username
        initial["email"] = self.request.user.email
        initial["full_name"] = self.request.user.full_name
        initial["pronouns"] = self.request.user.pronouns
        initial["date_of_birth"] = self.request.user.date_of_birth
        initial["major"] = self.request.user.major
        initial["interests"] = self.request.user.tags
        return initial

    def get_object(self, queryset=None):
        return get_object_or_404(SocialUser, username=self.kwargs["username"])


class DiscoverPageView(generic.ListView):
    model = ActivityPost
    template_name = "main/discover.html"

    def get_queryset(self):
        query = self.request.GET.get("q")

        button_action = self.request.GET.get("action")

        if button_action == "clear" or query is None:
            object_list = ActivityPost.objects.order_by("-timestamp")[:50]
        else:
            object_list = ActivityPost.get_posts_by_search(query)

        return object_list


class ConnectionsPageView(generic.DetailView):
    model = SocialUser
    template_name = "main/connections.html"

    def get_object(self, queryset=None):
        return get_object_or_404(SocialUser, username=self.kwargs.get("username"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_user"] = self.request.user
        context["active_requests"] = Connection.get_pending_connections(
            self.request.user
        )
        context["active_connections"] = Connection.get_active_connections(
            self.request.user
        )
        return context


class RequestConnectionView(generic.View):
    def get(self, request, *args, **kwargs):
        requester = get_object_or_404(SocialUser, username=self.request.user)
        receiver = get_object_or_404(SocialUser, username=self.kwargs["receiver"])

        if not Connection.are_connected(requester, receiver):
            Connection.objects.create(
                requester=requester,
                receiver=receiver,
                status=Connection.ConnectionStatus.REQUESTED,
            )

        return redirect(
            reverse_lazy("main:profile_page", kwargs={"username": receiver.username})
        )


class CancelConnectionView(generic.View):
    def get(self, request, *args, **kwargs):
        requester = get_object_or_404(SocialUser, username=self.kwargs["requester"])
        receiver = get_object_or_404(SocialUser, username=self.kwargs["receiver"])

        current_user = get_object_or_404(SocialUser, username=self.request.user)

        # Handles redirect differently since requester and receiver can both cancel the connection
        if current_user == requester and Connection.are_connected(requester, receiver):
            Connection.get_connection(requester, receiver).delete()

            return redirect(
                reverse_lazy(
                    "main:profile_page", kwargs={"username": receiver.username}
                )
            )
        elif current_user == receiver and Connection.are_connected(requester, receiver):
            Connection.objects.filter(requester=requester, receiver=receiver).delete()
            return redirect(reverse_lazy("main:home"))

        return redirect(reverse_lazy("main:home"))


class AcceptConnectionView(generic.View):
    def get(self, request, *args, **kwargs):
        requester = get_object_or_404(SocialUser, username=self.kwargs["requester"])
        receiver = get_object_or_404(SocialUser, username=self.kwargs["receiver"])

        if Connection.are_connected(requester, receiver):
            Connection.objects.filter(requester=requester, receiver=receiver).update(
                status=Connection.ConnectionStatus.CONNECTED
            )

        return redirect(
            reverse_lazy("main:connections", kwargs={"username": receiver.username})
        )


@login_required
def notifications(request, pk):
    template_name = "main/notifications.html"
    user_notifications = list(Notification.objects.filter(recipient_user=request.user))
    user_notifications.sort(key=lambda x: x.timestamp, reverse=True)
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
        return HttpResponseRedirect(reverse("main:profile_page", kwargs={"pk": pk}))
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

    connection = None
    try:
        # Check if a connection already exists in either direction
        connection = Connection.objects.get(
            Q(userA=request.user, userB=viewed_user)
            | Q(userA=viewed_user, userB=request.user)
        )
    except Connection.DoesNotExist:
        # If no connection exists, create a new one
        connection = Connection.objects.create(
            userA=request.user,
            userB=viewed_user,
            status=Connection.ConnectionStatus.REQUESTED_A_TO_B,
        )

    # Update the connection status
    connection.userA = request.user
    connection.userB = viewed_user
    connection.status = Connection.ConnectionStatus.REQUESTED_A_TO_B
    connection.save()

    # Create a new Notification object for userB
    notification_content = f"{request.user.username} wants to connect."
    notification = Notification.objects.create(
        recipient_user=connection.userB,
        from_user=request.user,
        content=notification_content,
        type=Notification.NotificationType.CONNECTION_REQUEST,
    )
    connection.notification = notification
    connection.save()

    return HttpResponseRedirect(reverse("main:profile_page", kwargs={"pk": pk}))


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
        if connection.notification:
            connection.notification.delete()
        connection.delete()
    return HttpResponseRedirect(reverse("main:profile_page", kwargs={"pk": pk}))


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
    try:
        # Find the connection, regardless of who initiated it
        connection = Connection.objects.get(
            Q(
                userA=request.user,
                userB=viewed_user,
                status=Connection.ConnectionStatus.CONNECTED,
            )
            | Q(
                userA=viewed_user,
                userB=request.user,
                status=Connection.ConnectionStatus.CONNECTED,
            )
        )
        connection.delete()
    except Connection.DoesNotExist:
        raise Http404("Connection not found.")
    return HttpResponseRedirect(reverse("main:connections", kwargs={"pk": pk}))


def search_view(request):
    form = SearchForm(request.GET or None)
    if "clear" in request.GET:
        results = ActivityPost.objects.all()
        tags = InterestTag.objects.all()
    elif form.is_valid():
        query = form.cleaned_data.get("query")
        query_tag = request.GET.get("tag")
        if query:
            results = ActivityPost.objects.filter(
                Q(title__contains=query) | Q(description__contains=query)
            )
            tags = InterestTag.objects.all()
        elif query_tag:
            results = ActivityPost.objects.filter(Q(tags__name=query_tag))
            tags = InterestTag.objects.filter(name__exact=query_tag)
            print(results)
        else:
            results = ActivityPost.objects.all()
            tags = InterestTag.objects.all()
    else:
        results = ActivityPost.objects.all()
        tags = InterestTag.objects.all()

    context = {
        "form": form,
        "results": results,
        "tags": tags,
    }
    return render(request, "main/discover.html", context)


@login_required
def delete_account(request):
    if request.method == "POST":
        user = SocialUser.objects.get(pk=request.user.pk)

        if "cancel" in request.POST:
            return redirect("main:home")
        else:
            user.delete()
            return redirect("login")
    else:
        context = {
            "title": "Delete Account",
        }
        return render(request, "main/delete_account.html", context)
