from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Task


class TaskForm(forms.ModelForm):
    """Form for creating and updating tasks with deadline validation."""

    class Meta:
        model = Task
        fields = ["title", "description", "deadline", "priority"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter task title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter task description (optional)",
                }
            ),
            "deadline": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional except title for inline quick-add
        for field_name in self.fields:
            if field_name != "title":
                self.fields[field_name].required = False

    def clean_deadline(self):
        """
        Validate that deadline is not in the past.

        For existing tasks, allows keeping a past deadline if it wasn't changed.
        This prevents validation errors when updating other fields on old tasks
        that already have past deadlines.

        Returns:
            datetime: The validated and timezone-aware deadline

        Raises:
            ValidationError: If a new or modified deadline is in the past
        """
        deadline = self.cleaned_data.get("deadline")
        if not deadline:
            return deadline

        # Ensure deadline is timezone-aware for accurate comparisons
        if timezone.is_naive(deadline):
            deadline = timezone.make_aware(deadline)

        # For existing tasks, check if deadline was actually changed
        if self.instance.pk:
            original_deadline = self.initial.get("deadline")
            if original_deadline:
                # Make original timezone-aware for comparison
                if timezone.is_naive(original_deadline):
                    original_deadline = timezone.make_aware(original_deadline)

                # Compare with small margin (60 seconds) to account for precision issues
                # If deadline wasn't changed, allow it even if it's in the past
                time_diff = abs((deadline - original_deadline).total_seconds())
                if time_diff < 60:  # Less than 1 minute difference = unchanged
                    return deadline

        # Validate that new or changed deadlines must be in the future
        if deadline < timezone.now():
            raise ValidationError("Deadline cannot be in the past.")

        return deadline
