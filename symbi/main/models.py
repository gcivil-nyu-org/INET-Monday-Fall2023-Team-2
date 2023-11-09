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
        OTHER = 4, _("Other")

    username = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField(default="2000-01-01")
    age = models.IntegerField(
        default=18, validators=[MinValueValidator(18), MaxValueValidator(150)]
    )
    major = models.CharField(max_length=100, default="undeclared")
    pronouns = models.IntegerField(default=Pronouns.OTHER, choices=Pronouns.choices)
    tags = models.ManyToManyField(InterestTag, related_name="tags")
    connections = models.ManyToManyField("SocialUser")


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

    class Meta:
        unique_together = ["userA", "userB"]

    def __str__(self) -> str:
        return self.text
