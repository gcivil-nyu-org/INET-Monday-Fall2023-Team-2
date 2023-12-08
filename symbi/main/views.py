from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .signals import user_blocked
from django.views.generic import DeleteView, TemplateView, DetailView

from posts.models import ActivityPost
from .models import SocialUser, Connection, Notification, Block, UserReport
from .forms import (
    SignupForm,
    LoginForm,
    EditProfileForm,
    ChangePasswordForm,
)


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
            user = form.save(commit=False)
            user.save()
            form.save_m2m()
            user.tags.set(form.cleaned_data["interests"])
            user.save()

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
        # Get posts where the user's interests are in the post tags
        interests_posts = ActivityPost.objects.filter(
            tags__in=self.request.user.tags.all(),
            status=ActivityPost.PostStatus.ACTIVE,
        )
        # Fetch users blocked by the logged-in user and users who have blocked the logged-in user
        blocked_users = Block.get_blocked_users(self.request.user)
        blocking_users = Block.get_blocking_users(self.request.user)

        context["interests_posts"] = interests_posts.exclude(
            poster__in=blocked_users
        ).exclude(poster__in=blocking_users)
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
        context["is_blocked"] = Block.get_blocked_status(self.request.user, self.object)

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

    def form_valid(self, form):
        user = form.save(commit=False)
        user.tags.set(form.cleaned_data["interests"])
        user.save()
        form.save_m2m()
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                parts = field.split("_")
                if len(parts) > 1:
                    field = f"{parts[0].capitalize()} {parts[1].capitalize()}"
                else:
                    field = field.capitalize()
                messages.error(self.request, f"{field}: {error}")

        return super().form_invalid(form)


@method_decorator(login_required, name="dispatch")
class DiscoverPageView(LoginRequiredMixin, generic.ListView):
    model = ActivityPost
    template_name = "main/discover.html"

    def get_queryset(self):
        query = self.request.GET.get("q")

        button_action = self.request.GET.get("action")

        # Fetch users blocked by the logged-in user and users who have blocked the logged-in user
        blocked_users = Block.get_blocked_users(self.request.user)
        blocking_users = Block.get_blocking_users(self.request.user)

        if button_action == "clear" or query is None:
            object_list = ActivityPost.objects.filter(
                ~Q(poster__in=blocked_users) & ~Q(poster__in=blocking_users)
            ).order_by("-timestamp")[:50]
        else:
            object_list = ActivityPost.get_posts_by_search(query).filter(
                ~Q(poster__in=blocked_users) & ~Q(poster__in=blocking_users)
            )

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
        current_user = request.user

        if "cancel" in request.POST:
            return redirect("main:home")
        else:
            current_user.delete()
            logout(request)
            return redirect("main:landing")
    else:
        context = {
            "title": "Delete Account",
        }
        return render(request, "main/delete_account.html", context)


@method_decorator(login_required, name="dispatch")
class BlockUserView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        current_user = get_object_or_404(SocialUser, username=self.request.user)
        user_to_block = get_object_or_404(
            SocialUser, username=self.kwargs["blocked_user"]
        )

        if current_user and user_to_block:
            # Check if the user is already blocked
            is_blocked = Block.objects.filter(
                blocker=current_user, blocked_user=user_to_block
            ).exists()

            if is_blocked:
                # If already blocked, unblock the user
                Block.objects.filter(
                    blocker=current_user, blocked_user=user_to_block
                ).delete()
            else:
                # If not blocked, then block the user
                Block.objects.create(blocker=current_user, blocked_user=user_to_block)
                # Trigger the 'user_blocked' signal upon blocking
                user_blocked.send(
                    sender=Block, blocker=current_user, blocked_user=user_to_block
                )

        return redirect(
            reverse_lazy(
                "main:profile_page", kwargs={"username": user_to_block.username}
            )
        )

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user can access the page being requested
        blocked_username = self.kwargs["blocked_user"]
        if self.request.user.username == blocked_username:
            # returns 403 Forbidden page
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


@login_required
def block_user(request, pk):
    current_user = request.user
    user_to_block = get_object_or_404(SocialUser, pk=pk)

    is_blocked = Block.objects.get_blocked_status(
        blocker=current_user, blocked_user=user_to_block
    )

    if is_blocked:
        # user_to_block is already blocked
        blocking_relation = Block.objects.get(
            blocker=current_user, blocked=user_to_block
        )
        blocking_relation.delete()
        return redirect(
            reverse_lazy(
                "main:profile_page", kwargs={"username": user_to_block.username}
            )
        )
    else:
        # block user_to_block
        Block.objects.create(blocker=current_user, blocked_user=user_to_block)
        return redirect(
            reverse_lazy(
                "main:profile_page", kwargs={"username": user_to_block.username}
            )
        )


class DeleteUserAccountView(LoginRequiredMixin, DeleteView):
    model = SocialUser
    template_name = "main/delete_account.html"
    success_url = reverse_lazy("main:landing")

    def get_object(self, queryset=None):
        return get_object_or_404(SocialUser, username=self.request.user.username)


@login_required
def blocked_users(request, pk):
    template_name = "main/blocked_users.html"
    current_user = request.user
    blocked_users = Block.get_blocked_users(blocker=current_user)

    # Sort blocked users by timestamp in descending order.
    blocked_users.sort(key=lambda x: x.timestamp, reverse=True)

    # Format timestamp for display
    time_differences = []
    now = timezone.now()
    for blocked_user in blocked_users:
        time_difference = now - blocked_user.timestamp
        # time_difference = format_time_difference(time_difference)
        time_differences.append(time_difference)

    zipped_blocked_users = zip(blocked_users, time_differences)

    context = {
        "current_user": current_user,
        "zipped_blocked_users": zipped_blocked_users,
    }
    return render(request, template_name, context)


@method_decorator(login_required, name="dispatch")
class BlockedUsersPageView(DetailView):
    model = SocialUser
    template_name = "main/blocked_users.html"

    def get_object(self, queryset=None):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        blocked_users = Block.objects.filter(blocker=current_user)
        context["blocked_users"] = blocked_users

        return context


@method_decorator(login_required, name="dispatch")
class SettingsPageView(LoginRequiredMixin, generic.DetailView):
    model = SocialUser
    template_name = "main/settings.html"

    def get_object(self, queryset=None):
        return get_object_or_404(SocialUser, username=self.kwargs.get("username"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_user"] = self.request.user

        return context

    def dispatch(self, request, *args, **kwargs):
        # Check if the logged-in user can access the page being requested
        viewed_username = self.kwargs["username"]
        if self.request.user.username != viewed_username:
            # returns 403 Forbidden page
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class ChangePasswordView(PasswordChangeView):
    form_class = ChangePasswordForm
    template_name = "main/change_password.html"
    success_url = reverse_lazy("main:change_password_done")

    def form_valid(self, form):
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class ChangePasswordDoneView(TemplateView):
    template_name = "main/change_password_done.html"



def user_reports_view(request):
    user_id = request.user.id  # Assuming 'user_id' is the ID of the user you want to retrieve reports for

    # Fetch all reports made by the user
    
    reported_posts = UserReport.objects.filter(
        reporter_id=user_id, reported_post__isnull=False
    ).select_related('reported_post')

    reported_comments = UserReport.objects.filter(
        reporter_id=user_id, reported_comment__isnull=False
    ).select_related('reported_comment__post')
    print("Reported Posts:")
    for report in reported_posts:
        print(f"Report ID: {report.id}")
        print(f"Reporter: {report.reporter}")
        print(f"Reported Post Title: {report.reported_post.title}")
        # Print other relevant details you want to see

    # Printing details for reported comments
    print("\nReported Comments:")
    for report in reported_comments:
        print(f"Report ID: {report.id}")
        print(f"Reporter: {report.reporter}")
        print(f"Reported Comment Text: {report.reported_comment.text}")
        
        
class UserReportedItemsView(DetailView):
    template_name = "main/user_reports.html"
    model = UserReport
    context_object_name = 'user_reports'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_reports = UserReport.objects.filter(reporter_id=self.kwargs.get('pk'))

        reported_comments = user_reports.filter(report_category=UserReport.ReportCategory.COMMENT).select_related('reported_comment__user')
        reported_posts = user_reports.filter(report_category=UserReport.ReportCategory.POST).select_related('reported_post__user')

        context['reported_comments'] = reported_comments
        context['reported_posts'] = reported_posts
        return context