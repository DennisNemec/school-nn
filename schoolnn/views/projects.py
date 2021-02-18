from typing import Optional

from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    DetailView,
    CreateView,
    ListView,
    DeleteView,
)

from schoolnn.models import Project


class ProjectCreateView(CreateView):
    """Responsible for the creation of projects."""

    class ProjectCreateForm(forms.ModelForm):
        class Meta:
            fields = ["name"]
            model = Project

    form_class = ProjectCreateForm
    template_name = "project/create_project.html"

    object: Optional[Project] = None

    def form_valid(self, form: ProjectCreateForm):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        if self.object is None:
            # TODO: Translation für Fehlermeldung
            raise ValueError("Failed to parse the project create form")

        return HttpResponseRedirect(self.get_success_url())


class ProjectListView(ListView):
    """Responsible for listing all projects."""

    queryset = Project.objects.order_by("-created_at")
    context_object_name = "projects"
    template_name = "project/project_overview.html"


class ProjectDetailView(DetailView):
    """Responsible for displaying a single project."""

    model = Project
    template_name = "project/project_details.html"


# TODO: Projekte editieren implementieren
class ProjectEditView(TemplateView):
    """Responsible for editing all the data of a project."""

    template_name = "project/edit_project.html"


class ProjectDeleteView(DeleteView):
    """Responsible for deleting all the data of a project."""

    model = Project
    success_url = reverse_lazy("project-list")
    template_name = "project/delete_project.html"
