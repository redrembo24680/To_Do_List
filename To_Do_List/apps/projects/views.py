from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ProjectForm
from .mixins import HTMXResponseMixin, ProjectQuerysetMixin
from .models import Project

if TYPE_CHECKING:
    pass
else:
    from apps.tasks.models import Task


class ProjectListView(LoginRequiredMixin, ProjectQuerysetMixin, ListView):
    """Display list of projects for the authenticated user."""

    model = Project
    context_object_name = "projects"
    template_name = "projects/project_list.html"

    def get_queryset(self):
        return self.get_project_queryset()


class ProjectsAllView(LoginRequiredMixin, ProjectQuerysetMixin, ListView):
    """Partial view for HTMX to load all projects with tasks."""

    model = Project
    context_object_name = "projects"
    template_name = "projects/partials/projects_all.html"

    def get_queryset(self):
        return self.get_project_queryset()


class ProjectListPartialView(LoginRequiredMixin, ListView):
    """Partial view for HTMX to load projects in sidebar."""

    model = Project
    context_object_name = "projects"
    template_name = "projects/partials/project_list_partial.html"

    def get_queryset(self):
        return Project.objects.for_user(self.request.user).select_related("owner")


class ProjectCreateView(LoginRequiredMixin, HTMXResponseMixin, CreateView):
    """Create a new project."""

    model = Project
    form_class = ProjectForm
    template_name = "projects/partials/project_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_update"] = False
        return context

    def form_valid(self, form):
        """
        Handle successful form submission with HTMX support.

        Sets the current user as the project owner and saves the project.

        For HTMX requests:
            - Returns an HTML fragment with updated projects list
            - Adds HX-Trigger header to notify client of successful creation
            - Client can listen to 'projectCreated' event for UI updates

        For regular requests:
            - Redirects to the project list page

        Args:
            form: Validated ProjectForm instance

        Returns:
            HttpResponse: HTML fragment for HTMX, or HttpResponseRedirect
        """
        form.instance.owner = self.request.user
        self.object = form.save()

        if self.request.htmx:
            return self.render_projects_list_htmx("projectCreated")

        return redirect("projects:project_list")


class ProjectUpdateView(LoginRequiredMixin, HTMXResponseMixin, UpdateView):
    """Update an existing project."""

    model = Project
    form_class = ProjectForm
    template_name = "projects/partials/project_form.html"

    def get_queryset(self):
        return Project.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_update"] = True
        return context

    def form_valid(self, form):
        self.object = form.save()
        if self.request.htmx:
            return self.render_projects_list_htmx("projectUpdated")
        return redirect("projects:project_detail", pk=self.object.pk)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a project."""

    model = Project

    def get_queryset(self):
        return Project.objects.for_user(self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.htmx:
            return HttpResponse("")
        return redirect("projects:project_list")


class ProjectDetailView(LoginRequiredMixin, ListView):
    """Display tasks for a specific project."""

    model = Task
    context_object_name = "tasks"
    template_name = "projects/partials/project_detail.html"

    def get_queryset(self):
        self.project = get_object_or_404(
            Project.objects.for_user(self.request.user), pk=self.kwargs["pk"]
        )
        return Task.objects.filter(project=self.project).select_related("project", "assigned_to")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context
