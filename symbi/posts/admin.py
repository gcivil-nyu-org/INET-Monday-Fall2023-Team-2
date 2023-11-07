from django.contrib import admin

from .models import ActivityPost


@admin.register(ActivityPost)
class ActivityPostAdmin(admin.ModelAdmin):
    list_display = ["poster", "title", "description", "status", "display_tags"]
    search_fields = ["poster", "title", "description", "status"]

    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
