from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from apps.projects.models import Project

from .forms import TaskForm
from .mixins import TaskHTMXMixin
from .models import Task


class TaskCreateView(LoginRequiredMixin, TaskHTMXMixin, CreateView):
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
            return self.render_task_item_htmx(task)

        self.object = form.save()
        if self.request.htmx:
            return redirect("projects:project_list")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        context["is_update"] = False
        return context


class TaskUpdateView(LoginRequiredMixin, TaskHTMXMixin, UpdateView):
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
            return self.render_task_item_htmx(
                self.object, trigger_event="taskUpdated", retarget=f"#task-{self.object.pk}"
            )
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


class TaskToggleView(LoginRequiredMixin, TaskHTMXMixin, UpdateView):
    """Toggle task completion status."""

    model = Task

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user).select_related(
            "project", "assigned_to"
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_done = not self.object.is_done
        self.object.save(update_fields=["is_done"])

        if request.htmx:
            return self.render_task_item_htmx(self.object)

        return redirect("projects:project_detail", pk=self.object.project.pk)
