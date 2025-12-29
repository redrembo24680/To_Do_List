from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ProjectForm
from .models import Project


class ProjectListView(LoginRequiredMixin, ListView):
    """Display list of projects for the authenticated user."""

    model = Project
    context_object_name = "projects"
    template_name = "projects/project_list.html"

    def get_queryset(self):
        from apps.tasks.models import Task

        tasks_prefetch = Prefetch(
            "tasks",
            queryset=Task.objects.select_related("assigned_to").order_by(
                "-priority", "deadline", "-created_at"
            ),
        )
        return (
            Project.objects.for_user(self.request.user)
            .select_related("owner")
            .prefetch_related(tasks_prefetch)
        )


class ProjectsAllView(LoginRequiredMixin, ListView):
    """Partial view for HTMX to load all projects with tasks."""

    model = Project
    context_object_name = "projects"
    template_name = "projects/partials/projects_all.html"

    def get_queryset(self):
        from apps.tasks.models import Task

        tasks_prefetch = Prefetch(
            "tasks",
            queryset=Task.objects.select_related("assigned_to").order_by(
                "-priority", "deadline", "-created_at"
            ),
        )
        return (
            Project.objects.for_user(self.request.user)
            .select_related("owner")
            .prefetch_related(tasks_prefetch)
        )


class ProjectListPartialView(LoginRequiredMixin, ListView):
    """Partial view for HTMX to load projects in sidebar."""

    model = Project
    context_object_name = "projects"
    template_name = "projects/partials/project_list_partial.html"

    def get_queryset(self):
        return Project.objects.for_user(self.request.user).select_related("owner")


class ProjectCreateView(LoginRequiredMixin, CreateView):
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
            # Return updated projects list as an HTML fragment
            projects = (
                Project.objects.for_user(self.request.user)
                .select_related("owner")
                .prefetch_related("tasks")
            )
            html = render_to_string(
                "projects/partials/projects_all.html", {"projects": projects}, request=self.request
            )

            # Add HX-Trigger header to notify client-side JavaScript
            response = HttpResponse(html)
            response["HX-Trigger"] = "projectCreated"
            return response

        return redirect("projects:project_list")


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
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
            # Return updated projects list
            projects = (
                Project.objects.for_user(self.request.user)
                .select_related("owner")
                .prefetch_related("tasks")
            )
            html = render_to_string(
                "projects/partials/projects_all.html", {"projects": projects}, request=self.request
            )
            response = HttpResponse(html)
            response["HX-Trigger"] = "projectUpdated"
            return response
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
            from django.http import HttpResponse

            return HttpResponse("")
        return redirect("projects:project_list")


class ProjectDetailView(LoginRequiredMixin, ListView):
    """Display tasks for a specific project."""

    model = None
    context_object_name = "tasks"
    template_name = "projects/partials/project_detail.html"

    def get_queryset(self):
        from apps.tasks.models import Task

        self.project = get_object_or_404(
            Project.objects.for_user(self.request.user), pk=self.kwargs["pk"]
        )
        return Task.objects.filter(project=self.project).select_related("project", "assigned_to")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context
