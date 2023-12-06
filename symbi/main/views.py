from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from posts.models import ActivityPost
from .models import SocialUser, Connection, Notification
from .forms import SignupForm, LoginForm, EditProfileForm


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

    def form_invalid(self, form):
        print(form.errors.as_json())
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        return super().form_invalid(form)


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
                    messages.error(request, f"{error}")

            return render(request, "main/signup.html", {"form": form})


class LogoutView(generic.RedirectView):
    url = reverse_lazy("main:landing")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class HomePageView(LoginRequiredMixin, generic.ListView):
    model = ActivityPost
    template_name = "main/home.html"

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


@method_decorator(login_required, name="dispatch")
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


@method_decorator(login_required, name="dispatch")
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
        initial["interests"] = self.request.user.tags.all()
        return initial

    def get_object(self, queryset=None):
        return get_object_or_404(SocialUser, username=self.kwargs["username"])

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user can access the page being requested
        viewed_username = self.kwargs["username"]
        if self.request.user.username != viewed_username:
            # returns 403 Forbidden page
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class DiscoverPageView(LoginRequiredMixin, generic.ListView):
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


@method_decorator(login_required, name="dispatch")
class ConnectionsPageView(LoginRequiredMixin, generic.DetailView):
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

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user can access the page being requested
        viewed_username = self.kwargs["username"]
        if self.request.user.username != viewed_username:
            # returns 403 Forbidden page
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class RequestConnectionView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        requester = get_object_or_404(SocialUser, username=self.request.user)
        receiver = get_object_or_404(SocialUser, username=self.kwargs["receiver"])

        if not Connection.are_connected(requester, receiver):
            connection = Connection.objects.create(
                requester=requester,
                receiver=receiver,
                status=Connection.ConnectionStatus.REQUESTED,
            )
            # Create a new Notification object for userB
            notification_content = f"{requester.username} wants to connect."
            notification = Notification.objects.create(
                recipient_user=connection.receiver,
                from_user=connection.requester,
                content=notification_content,
                type=Notification.NotificationType.CONNECTION_REQUEST,
            )
            print(notification.content)
            connection.notification = notification
            connection.save()

        return redirect(
            reverse_lazy("main:profile_page", kwargs={"username": receiver.username})
        )


@method_decorator(login_required, name="dispatch")
class CancelConnectionView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        requester = get_object_or_404(SocialUser, username=self.kwargs["requester"])
        receiver = get_object_or_404(SocialUser, username=self.kwargs["receiver"])

        current_user = get_object_or_404(SocialUser, username=self.request.user)

        # Handles redirect differently since requester and receiver can both cancel the connection
        if current_user == requester and Connection.are_connected(requester, receiver):
            connection = Connection.get_connection(requester, receiver)
            if connection:
                if connection.notification:
                    connection.notification.delete()
                connection.delete()

            return redirect(
                reverse_lazy(
                    "main:profile_page", kwargs={"username": receiver.username}
                )
            )
        elif current_user == receiver and Connection.are_connected(requester, receiver):
            connection = Connection.objects.filter(
                requester=requester, receiver=receiver
            ).first()
            if connection:
                if connection.notification:
                    connection.notification.delete()
                connection.delete()

            return redirect(reverse_lazy("main:home"))

        return redirect(reverse_lazy("main:home"))


@method_decorator(login_required, name="dispatch")
class AcceptConnectionView(LoginRequiredMixin, generic.View):
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

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user can access the page being requested
        receiver = get_object_or_404(SocialUser, username=self.kwargs["receiver"])
        if self.request.user.username != receiver.username:
            # returns 403 Forbidden page
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class NotificationsPageView(LoginRequiredMixin, generic.DetailView):
    model = SocialUser
    template_name = "main/notifications.html"

    def get_object(self, queryset=None):
        return get_object_or_404(SocialUser, username=self.kwargs.get("username"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get unread notifications
        unread_notifications = Notification.get_unread_user_notifications(
            self.request.user
        )
        # mark them as read
        unread_notifications.update(is_read=True)
        # set context data
        context["current_user"] = self.request.user
        context["user_notifications"] = Notification.get_user_notifications(
            self.request.user
        )
        context["notification_types"] = Notification.NotificationType

        return context

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user can access the page being requested
        viewed_username = self.kwargs["username"]
        if self.request.user.username != viewed_username:
            # returns 403 Forbidden page
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


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
