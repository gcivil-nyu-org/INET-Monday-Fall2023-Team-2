from django.contrib import admin

from .models import InterestTag, SocialUser, Connection


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


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ["requester", "receiver", "status"]
    search_fields = ["requester", "receiver"]
