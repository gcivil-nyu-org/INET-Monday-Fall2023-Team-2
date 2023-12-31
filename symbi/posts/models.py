from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings

# from django.db.models.signals import post_save
# from django.dispatch import receiver

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

    @classmethod
    def get_posts_by_user(cls, user):
        return cls.objects.filter(poster=user)

    @classmethod
    def get_posts_by_search(cls, search_query):
        return cls.objects.filter(
            (
                models.Q(title__icontains=search_query)
                | models.Q(description__icontains=search_query)
            )
            & models.Q(status=ActivityPost.PostStatus.ACTIVE)
        )


class Comment(models.Model):
    post = models.ForeignKey(
        ActivityPost, on_delete=models.CASCADE, related_name="comments"
    )
    commentPoster = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    text = models.TextField()
    timestamp = models.DateTimeField("date commented")
    taggedUsers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="taggedUsers"
    )

    def __str__(self):
        return self.text


# @receiver(post_save, sender=Comment)
# def create_comment_notification(sender, instance, created, **kwargs):
#     if created and instance.commentPoster != instance.post.poster:
#         Notification.objects.create(
#             recipient_user=instance.post.poster,
#             from_user=instance.commentPoster,
#             content=f"@{instance.commentPoster} posted a new comment on your post "
#             f"{instance.post.title}: {instance.text}",
#             type=Notification.NotificationType.NEW_COMMENT,
#         )


class Report(models.Model):
    class ReportCategory(models.IntegerChoices):
        POST = 1, _("post")
        COMMENT = 2, _("comment")

    class Reason(models.IntegerChoices):
        HATE_SPEECH_OR_SYMBOLS = 1, _("Hate speech or symbols")
        ABUSE_AND_HARASSMENT = 2, _("Abuse and harassment")
        VIOLENCE_OR_DANGEROUS_ORGANIZATIONS = 3, _(
            "Violence or dangerous organizations"
        )
        PRIVACY = 4, _("Privacy")
        SPAM = 5, _("Spam")
        SENSITIVE_OR_DISTURBING_MEDIA = 6, _("Sensitive or Disturbing Media")
        SCAMS_OR_FRAUD = 7, _("Scams or Fraud")
        FALSE_INFORMATION = 8, _("False information")

    # stores the primary key of object being reported
    reported_object_id = models.PositiveIntegerField()
    report_count = models.IntegerField(default=1)

    # tracks number of times an object has been reported
    report_category = models.IntegerField(choices=ReportCategory.choices)
    reason = models.IntegerField(choices=Reason.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
