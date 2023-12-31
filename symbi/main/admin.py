from django.contrib import admin

from .models import InterestTag, SocialUser, Notification, Connection, Block, UserReport


@admin.register(InterestTag)
class InterestTagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(SocialUser)
class SocialUserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "full_name",
        "pronouns",
        "date_of_birth",
        "major",
    ]
    search_fields = ["username"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["recipient_user", "from_user", "is_read"]
    search_fields = ["recipient_user", "from_user", "is_read"]


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ["requester", "receiver", "status"]
    search_fields = ["requester", "receiver"]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ["blocker", "blocked_user"]
    search_fields = ["blocker", "blocked_user"]


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ["reporter", "content_type", "object_id", "report_category"]
    search_fields = ["reporter", "content_type", "object_id", "report_category"]
