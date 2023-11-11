from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings

from main.models import InterestTag


class ActivityPost(models.Model):
    class PostStatus(models.IntegerChoices):
        DRAFT = 1, _("Draft")
        ACTIVE = 2, _("Active")
        ARCHIVED = 3, _("Archived")

    class Meta:
        db_table = "activity_posts"
        verbose_name_plural = "Activity Posts"

    poster = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1023)
    status = models.IntegerField(default=PostStatus.DRAFT, choices=PostStatus.choices)
    tags = models.ManyToManyField(InterestTag)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:post_details_view", args=(str(self.id)))


class Comment(models.Model):
    post = models.ForeignKey(
        ActivityPost, on_delete=models.CASCADE, related_name="comments"
    )
    commentPoster = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1
    )
    text = models.TextField()
    timestamp = models.DateTimeField("date commented")

    def __str__(self):
        return self.text
