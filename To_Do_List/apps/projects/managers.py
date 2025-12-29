from django.db import models


class OwnedQuerySet(models.QuerySet):
    """QuerySet that filters objects by owner."""

    def for_user(self, user):
        """Filter queryset to only include objects owned by the given user."""
        return self.filter(owner=user)


class OwnedManager(models.Manager):
    """Manager that provides OwnedQuerySet."""

    def get_queryset(self):
        return OwnedQuerySet(self.model, using=self._db)

    def for_user(self, user):
        """Filter objects to only include those owned by the given user."""
        return self.get_queryset().for_user(user)
