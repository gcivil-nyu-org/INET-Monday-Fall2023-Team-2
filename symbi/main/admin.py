from django.contrib import admin

from .models import InterestTag


@admin.register(InterestTag)
class InterestTagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
