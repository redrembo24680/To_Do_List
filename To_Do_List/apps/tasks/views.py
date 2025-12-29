from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from apps.projects.models import Project

from .forms import TaskForm
from .models import Task


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Create a new task for a project."""

    model = Task
    form_class = TaskForm
    template_name = "tasks/partials/task_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(
            Project.objects.for_user(request.user), pk=kwargs["project_pk"]
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = self.project

        # Handle simple title-only creation from inline form
        if self.request.htmx and "title" in self.request.POST and len(self.request.POST) <= 3:
            # Simple inline creation
            task = form.save()
            html = render_to_string(
                "tasks/partials/task_item.html", {"task": task}, request=self.request
            )
            return HttpResponse(html)

        self.object = form.save()
        if self.request.htmx:
            # Return to project view
            from django.shortcuts import redirect

            return redirect("projects:project_list")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        context["is_update"] = False
        return context


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing task."""

    model = Task
    form_class = TaskForm
    template_name = "tasks/partials/task_form.html"

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user).select_related("project")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_update"] = True
        return context

    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            html = render_to_string(
                "tasks/partials/task_item.html", {"task": self.object}, request=self.request
            )
            response = HttpResponse(html)
            response["HX-Trigger"] = "taskUpdated"
            response["HX-Retarget"] = f"#task-{self.object.pk}"
            response["HX-Reswap"] = "outerHTML"
            return response
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("projects:project_detail", kwargs={"pk": self.object.project.pk})


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a task."""

    model = Task

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user).select_related("project")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse("")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("projects:project_detail", kwargs={"pk": self.object.project.pk})


class TaskToggleView(LoginRequiredMixin, UpdateView):
    """Toggle task completion status."""

    model = Task
    fields = ["is_done"]

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user).select_related(
            "project", "assigned_to"
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_done = not self.object.is_done
        self.object.save()

        if request.htmx:
            html = render_to_string(
                "tasks/partials/task_item.html", {"task": self.object}, request=request
            )
            return HttpResponse(html)

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("projects:project_detail", kwargs={"pk": self.object.project.pk})
