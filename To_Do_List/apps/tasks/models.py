import uuid

from django.conf import settings
from django.db import models


class Task(models.Model):
    """
    Task model with priority, deadline, and completion status.

    Tasks belong to projects and can be assigned to users. They support
    priority levels (Low, Medium, High) and optional deadlines. Tasks are
    ordered by priority (high to low), then deadline (soonest first).

    Attributes:
        id: UUID primary key for better security and distributed systems
        project: Parent project (cascade delete)
        title: Task name/description
        description: Optional detailed description
        deadline: Optional due date/time
        priority: Importance level (1=Low, 2=Medium, 3=High)
        is_done: Completion status
        assigned_to: Optional user assignment (null if unassigned or user deleted)
        created_at: Timestamp when task was created
        updated_at: Timestamp of last modification
    """

    class Priority(models.IntegerChoices):
        """Priority levels for tasks, ordered from low to high importance."""

        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,  # Indexed for ordering and filtering by deadline
    )
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,  # Indexed for ordering and filtering by priority
    )
    is_done = models.BooleanField(
        default=False,
        db_index=True,  # Indexed for filtering completed/incomplete tasks
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "deadline", "-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            # Composite index for the default ordering (priority desc, deadline asc)
            models.Index(fields=["-priority", "deadline"]),
            # Index for filtering tasks by project and completion status
            models.Index(fields=["project", "is_done"]),
        ]

    def __str__(self):
        return self.title
