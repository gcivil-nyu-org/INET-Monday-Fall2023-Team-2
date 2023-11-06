from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

from main.models import SocialUser


class ActivityTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class ActivityPost(models.Model):
    poster = models.ForeignKey(SocialUser, on_delete=models.CASCADE, default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    # Status values:
    # 1: Draft
    # 2: Posted
    # 3: Archived
    status = models.PositiveBigIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    tags = models.ManyToManyField(ActivityTag, related_name="tags")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("posts:post_details_view", args=(str(self.id)))


class Comment(models.Model):
    post = models.ForeignKey(
        ActivityPost, on_delete=models.CASCADE, related_name="comments"
    )
    poster = models.ForeignKey(SocialUser, on_delete=models.CASCADE, default=1)
    text = models.TextField()
    timestamp = models.DateTimeField("date commented")

    def __str__(self) -> str:
        return self.text
