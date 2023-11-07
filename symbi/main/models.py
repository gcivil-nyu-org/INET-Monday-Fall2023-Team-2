from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class InterestTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "interest_tags"
        verbose_name_plural = "Interest Tags"

    def __str__(self) -> str:
        return self.name


class SocialUser(AbstractUser):
    PRONOUN_CHOICES = (
        ("he/him", "He/Him"),
        ("she/her", "She/Her"),
        ("they/them", "They/Them"),
        ("other", "Other"),
    )

    username = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField(default="2000-01-01")
    age = models.IntegerField(
        default=18, validators=[MinValueValidator(18), MaxValueValidator(150)]
    )
    major = models.CharField(max_length=100, default="undeclared")
    pronouns = models.CharField(
        max_length=9, choices=PRONOUN_CHOICES, default="she/her"
    )
    tags = models.ManyToManyField(InterestTag, related_name="tags")
