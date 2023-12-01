from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse



class InterestTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "interest_tags"
        verbose_name_plural = "Interest Tags"

    def __str__(self):
        return self.name


class SocialUser(AbstractUser):
    class Pronouns(models.IntegerChoices):
        SHE = 1, _("She/Her")
        HE = 2, _("He/Him")
        THEY = 3, _("They/Them")
        OTHER = 4, _("Other/Prefer Not To Say")

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True, default="@nyu.edu")
    full_name = models.CharField(max_length=50, default="")
    pronouns = models.IntegerField(default=Pronouns.OTHER, choices=Pronouns.choices)
    date_of_birth = models.DateField(null=True)
    major = models.CharField(max_length=100, default="undeclared")
    tags = models.ManyToManyField(InterestTag, related_name="tags")
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    timestamp = models.DateTimeField("timestamp", default=timezone.now)  # joined

    def get_absolute_url(self):
        return reverse("main:profile_page", args=(str(self.username)))

class Notification(models.Model):
    class NotificationType(models.IntegerChoices):
        CONNECTION_REQUEST = 1, _("Connection Request")
        NEW_COMMENT = 2, _("New Comment")

    recipient_user = models.ForeignKey(
        SocialUser, on_delete=models.CASCADE, related_name="recipient_user"
    )
    from_user = models.ForeignKey(
        SocialUser, on_delete=models.CASCADE, related_name="from_user"
    )
    content = models.TextField()
    timestamp = models.DateTimeField("timestamp", default=timezone.now)
    is_read = models.BooleanField(default=False)
    type = models.IntegerField(choices=NotificationType.choices)

    # Get all notifications for a user
    @classmethod
    def get_user_notifications(cls, user):
        return cls.objects.filter(models.Q(recipient_user=user)).all()


class Connection(models.Model):
    class ConnectionStatus(models.IntegerChoices):
        NOT_CONNECTED = 1, _("Not Connected")
        REQUESTED = 2, _("Requested")
        CONNECTED = 3, _("Connected")
        BLOCKED = 4, _("Blocked")

    requester = models.ForeignKey(
        SocialUser, on_delete=models.CASCADE, related_name="requester"
    )
    receiver = models.ForeignKey(
        SocialUser, on_delete=models.CASCADE, related_name="receiver"
    )
    timestamp = models.DateTimeField("timestamp", default=timezone.now)
    status = models.IntegerField(
        default=ConnectionStatus.NOT_CONNECTED, choices=ConnectionStatus.choices
    )
    # ensure related notification is also deleted when the connection request is canceled
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        unique_together = ["requester", "receiver"]

    # Check if two users are connected
    @classmethod
    def are_connected(cls, user1, user2):
        return cls.objects.filter(
            (models.Q(requester=user1) & models.Q(receiver=user2))
            | (models.Q(requester=user2) & models.Q(receiver=user1))
        ).exists()

    # Get all connection objects regardless of who is requester and receiver
    @classmethod
    def get_connection(cls, user1, user2):
        return cls.objects.filter(
            (models.Q(requester=user1) & models.Q(receiver=user2))
            | (models.Q(requester=user2) & models.Q(receiver=user1))
        ).first()

    # Get all connections where the user was the receiver
    @classmethod
    def get_pending_connections(cls, user):
        return (
            cls.objects.filter(receiver=user)
            .filter(status=Connection.ConnectionStatus.REQUESTED)
            .all()
        )

    # Get all active connections for a user
    @classmethod
    def get_active_connections(cls, user):
        return cls.objects.filter(
            (models.Q(requester=user) | models.Q(receiver=user))
            & models.Q(status=Connection.ConnectionStatus.CONNECTED)
        ).all()

    def __str__(self):
        return f"{self.requester} - {self.receiver}"
