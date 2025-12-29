"""Mixins for task views."""

from django.http import HttpResponse
from django.template.loader import render_to_string


class TaskHTMXMixin:
    """Mixin to handle HTMX responses for task views."""

    def render_task_item_htmx(
        self, task, trigger_event: str | None = None, retarget: str | None = None
    ) -> HttpResponse:
        """
        Render task item for HTMX response.

        Args:
            task: Task instance to render
            trigger_event: Optional HTMX event name to trigger
            retarget: Optional HTMX retarget selector

        Returns:
            HttpResponse with task item HTML
        """
        html = render_to_string(
            "tasks/partials/task_item.html", {"task": task}, request=self.request
        )
        response = HttpResponse(html)
        if trigger_event:
            response["HX-Trigger"] = trigger_event
        if retarget:
            response["HX-Retarget"] = retarget
            response["HX-Reswap"] = "outerHTML"
        return response
