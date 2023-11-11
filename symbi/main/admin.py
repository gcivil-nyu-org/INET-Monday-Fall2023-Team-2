from django.contrib import admin

from .models import InterestTag, SocialUser


@admin.register(InterestTag)
class InterestTagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(SocialUser)
class SocialUserAdmin(admin.ModelAdmin):
    list_display = ["username", "date_of_birth", "age", "major", "pronouns"]
    search_fields = ["username"]
