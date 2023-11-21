from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


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


class Connection(models.Model):
    class ConnectionStatus(models.IntegerChoices):
        NOT_CONNECTED = 1, _("Not Connected")
        REQUESTED_A_TO_B = 2, _("Requested A -> B")
        CONNECTED = 3, _("Connected")
        BLOCKED = 4, _("Blocked")

    userA = models.ForeignKey(
        SocialUser, on_delete=models.CASCADE, related_name="userA"
    )
    userB = models.ForeignKey(
        SocialUser, on_delete=models.CASCADE, related_name="userB"
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
        unique_together = ["userA", "userB"]

    def __str__(self) -> str:
        return self.text
