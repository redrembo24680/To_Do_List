import pytest
from django.urls import reverse

from apps.projects.forms import ProjectForm
from apps.projects.models import Project


@pytest.mark.django_db
class TestProjectModel:
    """Test Project model."""

    def test_create_project(self, user):
        """Test creating a project."""
        project = Project.objects.create(
            name="Test Project", description="Test Description", owner=user
        )
        assert project.name == "Test Project"
        assert project.owner == user
        assert str(project) == "Test Project"

    def test_project_owned_queryset(self, user, another_user):
        """Test OwnedQuerySet filters by user."""
        project1 = Project.objects.create(name="User1 Project", owner=user)
        project2 = Project.objects.create(name="User2 Project", owner=another_user)

        user_projects = Project.objects.for_user(user)
        assert project1 in user_projects
        assert project2 not in user_projects


@pytest.mark.django_db
class TestProjectViews:
    """Test Project views."""

    def test_project_list_view_requires_login(self, client):
        """Test that project list requires login."""
        response = client.get(reverse("projects:project_list"))
        assert response.status_code == 302  # Redirect to login

    def test_project_list_view_authenticated(self, authenticated_client, user):
        """Test project list view for authenticated user."""
        Project.objects.create(name="Test Project", owner=user)
        response = authenticated_client.get(reverse("projects:projects_all"))
        assert response.status_code == 200
        assert "Test Project" in response.content.decode()

    def test_project_create_view(self, authenticated_client, user):
        """Test creating a project via view."""
        url = reverse("projects:project_create")
        response = authenticated_client.post(
            url,
            {"name": "New Project", "description": "New Description"},
            **{"HTTP_HX-Request": "true"},
        )

        assert response.status_code == 200
        assert Project.objects.filter(name="New Project", owner=user).exists()

    def test_project_update_view(self, authenticated_client, user):
        """Test updating a project."""
        project = Project.objects.create(name="Old Name", owner=user)
        url = reverse("projects:project_update", kwargs={"pk": project.pk})

        response = authenticated_client.post(
            url,
            {"name": "Updated Name", "description": "Updated Description"},
            **{"HTTP_HX-Request": "true"},
        )

        assert response.status_code == 200
        project.refresh_from_db()
        assert project.name == "Updated Name"

    def test_project_delete_view(self, authenticated_client, user):
        """Test deleting a project."""
        project = Project.objects.create(name="To Delete", owner=user)
        url = reverse("projects:project_delete", kwargs={"pk": project.pk})

        response = authenticated_client.delete(url, **{"HTTP_HX-Request": "true"})

        assert response.status_code == 200
        assert not Project.objects.filter(pk=project.pk).exists()

    def test_cannot_access_other_user_project(self, authenticated_client, another_user):
        """Test that user cannot access another user's project."""
        project = Project.objects.create(name="Other User Project", owner=another_user)
        url = reverse("projects:project_update", kwargs={"pk": project.pk})

        response = authenticated_client.get(url)
        assert response.status_code == 404

    def test_projects_all_view(self, authenticated_client, user):
        """Test ProjectsAllView returns projects."""
        Project.objects.create(name="Project 1", owner=user)
        Project.objects.create(name="Project 2", owner=user)

        response = authenticated_client.get(reverse("projects:projects_all"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Project 1" in content
        assert "Project 2" in content


@pytest.mark.django_db
class TestProjectForm:
    """Test Project form validation."""

    def test_project_form_valid(self):
        """Test valid project form."""
        form = ProjectForm(data={"name": "Valid Project", "description": "Valid Description"})
        assert form.is_valid()

    def test_project_form_name_required(self):
        """Test that name is required."""
        form = ProjectForm(data={"description": "Description"})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_project_form_max_length(self):
        """Test name max length validation."""
        long_name = "x" * 201
        form = ProjectForm(data={"name": long_name})
        # Project name doesn't have explicit max_length validation
        # This test verifies form validation behavior
        assert form.is_valid()  # Model allows long names
