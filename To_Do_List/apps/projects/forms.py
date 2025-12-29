from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects."""

    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter project name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter project description (optional)",
                }
            ),
        }
