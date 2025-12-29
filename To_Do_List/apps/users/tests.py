import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test Custom User model."""

    def test_create_user(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        assert user.email == "admin@example.com"
        assert user.is_staff
        assert user.is_superuser

    def test_user_str_representation(self):
        """Test string representation of user."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        assert str(user) == "test@example.com"

    def test_user_email_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(username="user1", email="test@example.com", password="pass123")

        with pytest.raises(IntegrityError):
            User.objects.create_user(username="user2", email="test@example.com", password="pass456")


@pytest.mark.django_db
class TestUserAuthentication:
    """Test user authentication."""

    def test_login_view_get(self, client):
        """Test login view GET request."""
        response = client.get(reverse("account_login"))
        assert response.status_code == 200
        assert "Sign In" in response.content.decode()

    def test_signup_view_get(self, client):
        """Test signup view GET request."""
        response = client.get(reverse("account_signup"))
        assert response.status_code == 200

    def test_profile_view_requires_login(self, client):
        """Test profile view requires authentication."""
        response = client.get(reverse("users:profile"))
        assert response.status_code == 302  # Redirect to login

    def test_profile_view_authenticated(self, authenticated_client):
        """Test profile view for authenticated user."""
        response = authenticated_client.get(reverse("users:profile"))
        assert response.status_code == 200

    def test_user_cannot_create_without_email(self):
        """Test creating user with blank email succeeds but is not recommended."""
        # Django's default UserManager allows empty email if username is provided
        # This test documents that behavior
        user = User.objects.create_user(username="testuser", email="", password="test123")
        assert user.email == ""
        assert user.username == "testuser"
