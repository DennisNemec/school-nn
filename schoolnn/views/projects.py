from typing import Optional

from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, resolve
from django.views import View
from django.views.generic import DetailView, CreateView, ListView, DeleteView

from schoolnn.models import Project, Dataset, Architecture


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


class ProjectEditView(View):
    """Responsible for editing all the data of a project."""

    template_name: str = "project/edit_project.html"

    def get(self, request, *args, **kwargs):
        self._setup()

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self._setup()

        if self.step == "dataset":
            self.project.dataset_id = request.POST.get("dataset")
            messages.success(request, "Datensatz erfolgreich gewählt")
        else:
            self.project.name = request.POST.get("name")
            messages.success(request, "Projekteinstellungen gespeichert")

        self.project.save()

        return redirect("project-details", self.kwargs["pk"])

    def _setup(self):
        self.step = self._get_step()
        self.project = self._get_project()
        self.context = {"step": self.step, "project": self.project}
        self.context = {**self.context, **self._get_step_data()}

    # project-edit-dataset -> dataset
    def _get_step(self):
        url_name = resolve(self.request.path_info).url_name
        return url_name.split("-")[-1]

    def _get_project(self):
        return Project.objects.get(pk=self.kwargs["pk"])

    def _get_step_data(self):
        if self.step == "dataset":
            return {"datasets": Dataset.objects.all()}
        elif self.step == "architecture":
            return {"architectures": Architecture.objects.all()}
        else:
            return {}


class ProjectDeleteView(DeleteView):
    """Responsible for deleting all the data of a project."""

    model = Project
    success_url = reverse_lazy("project-list")
    template_name = "project/delete_project.html"
