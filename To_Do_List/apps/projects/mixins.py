"""Mixins for project views."""

from django.db.models import Prefetch
from django.http import HttpResponse
from django.template.loader import render_to_string


class ProjectQuerysetMixin:
    """Mixin to provide common queryset logic for project views."""

    def get_project_queryset(self):
        """Get projects queryset with optimized prefetching."""
        from apps.tasks.models import Task

        tasks_prefetch = Prefetch(
            "tasks",
            queryset=Task.objects.select_related("assigned_to").order_by(
                "-priority", "deadline", "-created_at"
            ),
        )
        return (
            self.model.objects.for_user(self.request.user)
            .select_related("owner")
            .prefetch_related(tasks_prefetch)
        )


class HTMXResponseMixin:
    """Mixin to handle HTMX responses consistently."""

    def render_htmx_response(
        self, template_name: str, context: dict, trigger_event: str | None = None
    ) -> HttpResponse:
        """
        Render HTMX response with optional event trigger.

        Args:
            template_name: Template to render
            context: Context data for template
            trigger_event: Optional HTMX event name to trigger

        Returns:
            HttpResponse with rendered template and optional HX-Trigger header
        """
        html = render_to_string(template_name, context, request=self.request)
        response = HttpResponse(html)
        if trigger_event:
            response["HX-Trigger"] = trigger_event
        return response

    def render_projects_list_htmx(self, trigger_event: str) -> HttpResponse:
        """
        Render projects list for HTMX response.

        Args:
            trigger_event: HTMX event name to trigger

        Returns:
            HttpResponse with projects list
        """
        from .models import Project

        projects = (
            Project.objects.for_user(self.request.user)
            .select_related("owner")
            .prefetch_related("tasks")
        )
        return self.render_htmx_response(
            "projects/partials/projects_all.html",
            {"projects": projects},
            trigger_event=trigger_event,
        )
