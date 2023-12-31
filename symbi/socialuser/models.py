from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

PRONOUN_CHOICES = (
    ("he/him", "He/Him"),
    ("she/her", "She/Her"),
    ("they/them", "They/Them"),
    ("other", "Other"),
)


class InterestTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class SocialUser(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    age = models.IntegerField(
        default=18, validators=[MinValueValidator(18), MaxValueValidator(150)]
    )
    major = models.CharField(max_length=100)
    # Pronouns values:
    # 1: she/her
    # 2: he/him
    # 3: they/them
    # 4: other
    # pronouns = models.PositiveBigIntegerField(
    #     default=1, validators=[MinValueValidator(1), MaxValueValidator(4)]
    # )
    pronouns = models.CharField(
        max_length=9, choices=PRONOUN_CHOICES, default="she/her"
    )
    tags = models.ManyToManyField(InterestTag, related_name="tags")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("socialuser:profile_view", args=(str(self.id)))


class Connection(models.Model):
    socialuser = models.ForeignKey(
        SocialUser, on_delete=models.CASCADE, related_name="connections"
    )
    # userB = models.ForeignKey(User, on_delete=models.CASCADE) # who this connection is with
    userB_id = models.CharField(max_length=20)  # who this connection is with
    timestamp = models.DateTimeField("date connected")
    # Status values:
    # 1: Not Connected
    # 2: Requested A -> B
    # 3: Requested B -> A
    # 4: Connected
    # 5: Blocked
    status = models.PositiveBigIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self) -> str:
        return self.text
