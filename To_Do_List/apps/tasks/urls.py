from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("<uuid:project_pk>/create/", views.TaskCreateView.as_view(), name="task_create"),
    path("<uuid:pk>/update/", views.TaskUpdateView.as_view(), name="task_update"),
    path("<uuid:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    path("<uuid:pk>/toggle/", views.TaskToggleView.as_view(), name="task_toggle"),
]
