from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.projects.models import Project
from apps.tasks.forms import TaskForm
from apps.tasks.models import Task


@pytest.mark.django_db
class TestTaskModel:
    """Test Task model."""

    def test_create_task(self, user):
        """Test creating a task."""
        project = Project.objects.create(name="Test Project", owner=user)
        task = Task.objects.create(
            project=project,
            title="Test Task",
            description="Test Description",
            priority=Task.Priority.HIGH,
        )
        assert task.title == "Test Task"
        assert task.priority == Task.Priority.HIGH
        assert str(task) == "Test Task"

    def test_task_default_priority(self, user):
        """Test task has default priority."""
        project = Project.objects.create(name="Test Project", owner=user)
        task = Task.objects.create(project=project, title="Test Task")
        assert task.priority == Task.Priority.MEDIUM

    def test_task_is_done_default(self, user):
        """Test task is_done defaults to False."""
        project = Project.objects.create(name="Test Project", owner=user)
        task = Task.objects.create(project=project, title="Test Task")
        assert task.is_done is False

    def test_task_ordering(self, user):
        """Test tasks are ordered by priority and deadline."""
        project = Project.objects.create(name="Test Project", owner=user)

        task1 = Task.objects.create(
            project=project, title="Low Priority", priority=Task.Priority.LOW
        )
        task2 = Task.objects.create(
            project=project, title="High Priority", priority=Task.Priority.HIGH
        )

        tasks = list(Task.objects.all())
        assert tasks[0] == task2  # High priority first
        assert tasks[1] == task1


@pytest.mark.django_db
class TestTaskForm:
    """Test Task form validation."""

    def test_task_form_valid(self, user):
        """Test valid task form."""
        future_date = timezone.now() + timedelta(days=1)

        form = TaskForm(
            data={
                "title": "New Task",
                "description": "Description",
                "deadline": future_date,
                "priority": Task.Priority.HIGH,
            }
        )
        assert form.is_valid()

    def test_task_form_deadline_in_past_for_new_task(self, user):
        """Test that deadline in past is invalid for new tasks."""
        past_date = timezone.now() - timedelta(days=1)

        form = TaskForm(
            data={"title": "New Task", "deadline": past_date, "priority": Task.Priority.MEDIUM}
        )
        assert not form.is_valid()
        assert "deadline" in form.errors

    def test_task_form_title_required(self):
        """Test that title is required."""
        form = TaskForm(data={"description": "Description"})
        assert not form.is_valid()
        assert "title" in form.errors


@pytest.mark.django_db
class TestTaskViews:
    """Test Task views."""

    def test_task_create_view_inline(self, authenticated_client, user):
        """Test creating a task via inline form."""
        project = Project.objects.create(name="Test Project", owner=user)
        url = reverse("tasks:task_create", kwargs={"project_pk": project.pk})

        response = authenticated_client.post(
            url, {"title": "New Task", "csrfmiddlewaretoken": "test"}, **{"HTTP_HX-Request": "true"}
        )

        assert response.status_code == 200
        assert Task.objects.filter(title="New Task", project=project).exists()

    def test_task_update_view(self, authenticated_client, user):
        """Test updating a task."""
        project = Project.objects.create(name="Test Project", owner=user)
        task = Task.objects.create(project=project, title="Old Title", priority=Task.Priority.LOW)

        url = reverse("tasks:task_update", kwargs={"pk": task.pk})
        future_date = timezone.now() + timedelta(days=1)

        response = authenticated_client.post(
            url,
            {
                "title": "Updated Title",
                "priority": Task.Priority.HIGH,
                "deadline": future_date.strftime("%Y-%m-%dT%H:%M"),
            },
            **{"HTTP_HX-Request": "true"},
        )

        assert response.status_code == 200
        task.refresh_from_db()
        assert task.title == "Updated Title"
        assert task.priority == Task.Priority.HIGH

    def test_task_delete_view(self, authenticated_client, user):
        """Test deleting a task."""
        project = Project.objects.create(name="Test Project", owner=user)
        task = Task.objects.create(project=project, title="To Delete")

        url = reverse("tasks:task_delete", kwargs={"pk": task.pk})
        response = authenticated_client.delete(url, **{"HTTP_HX-Request": "true"})

        assert response.status_code == 200
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_task_toggle_view(self, authenticated_client, user):
        """Test toggling task completion."""
        project = Project.objects.create(name="Test Project", owner=user)
        task = Task.objects.create(project=project, title="Test Task", is_done=False)

        url = reverse("tasks:task_toggle", kwargs={"pk": task.pk})
        response = authenticated_client.post(
            url, {"is_done": "true"}, **{"HTTP_HX-Request": "true"}
        )

        assert response.status_code == 200
        task.refresh_from_db()
        assert task.is_done is True

    def test_cannot_access_other_user_task(self, authenticated_client, another_user):
        """Test that user cannot access another user's task."""
        project = Project.objects.create(name="Other User Project", owner=another_user)
        task = Task.objects.create(project=project, title="Other User Task")

        url = reverse("tasks:task_update", kwargs={"pk": task.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 404

    def test_task_create_full_form(self, authenticated_client, user):
        """Test creating task with full form modal."""
        project = Project.objects.create(name="Test Project", owner=user)
        url = reverse("tasks:task_create", kwargs={"project_pk": project.pk})
        future_date = timezone.now() + timedelta(days=1)

        response = authenticated_client.post(
            url,
            {
                "title": "Full Form Task",
                "description": "Full description",
                "priority": Task.Priority.HIGH,
                "deadline": future_date.strftime("%Y-%m-%dT%H:%M"),
            },
            **{"HTTP_HX-Request": "true"},
        )

        # Response may be redirect or HTMX response
        assert response.status_code in [200, 302]
        assert Task.objects.filter(title="Full Form Task", project=project).exists()
        task = Task.objects.get(title="Full Form Task")
        assert task.description == "Full description"
        assert task.priority == Task.Priority.HIGH
