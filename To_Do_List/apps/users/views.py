"""Views for users app."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view."""

    template_name = "users/profile.html"
