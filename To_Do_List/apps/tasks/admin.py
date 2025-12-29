from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "priority", "deadline", "is_done", "created_at"]
    list_filter = ["priority", "is_done", "created_at", "deadline"]
    search_fields = ["title", "description", "project__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["project", "assigned_to"]
    list_editable = ["is_done"]
