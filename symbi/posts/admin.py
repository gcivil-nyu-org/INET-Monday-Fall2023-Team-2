from django.contrib import admin

from .models import ActivityPost, Report


@admin.register(ActivityPost)
class ActivityPostAdmin(admin.ModelAdmin):
    list_display = ["poster", "title", "description", "status", "display_tags"]
    search_fields = ["poster", "title", "description", "status"]

    def display_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):  
    list_display = ["reported_object_id", "report_count", "report_category"]
    search_fields = ["reported_object_id", "report_count", "report_category"]
