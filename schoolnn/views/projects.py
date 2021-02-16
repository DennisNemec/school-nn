from django.views.generic import TemplateView, DetailView

from schoolnn.models import Project


class ProjectCreateView(TemplateView):
    """Responsible for the creation of projects."""

    template_name = "project/create_project.html"


class ProjectListView(TemplateView):
    """Responsible for listing all projects."""

    template_name = "project/project_overview.html"


class ProjectDetailView(DetailView):
    """Responsible for displaying a single project."""

    model = Project
    template_name = "project/project_details.html"


class ProjectEditView(TemplateView):
    """Responsible for editing all the data of a project."""

    template_name = "project/edit_project.html"
