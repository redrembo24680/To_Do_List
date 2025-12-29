from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    # Project URLs
    path("", views.ProjectListView.as_view(), name="project_list"),
    path("all/", views.ProjectsAllView.as_view(), name="projects_all"),
    path("partial/", views.ProjectListPartialView.as_view(), name="project_list_partial"),
    path("create/", views.ProjectCreateView.as_view(), name="project_create"),
    path("<uuid:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("<uuid:pk>/update/", views.ProjectUpdateView.as_view(), name="project_update"),
    path("<uuid:pk>/delete/", views.ProjectDeleteView.as_view(), name="project_delete"),
]
