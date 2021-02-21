import json
from typing import Optional

from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, resolve
from django.views import View
from django.views.generic import DetailView, CreateView, ListView, DeleteView

from schoolnn.models import Project, Dataset, Architecture
from schoolnn.resources.static.layer_list import layer_list


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
        post_redirect: Optional[HttpResponseRedirect] = None
        self._setup()

        if self.step == "dataset":
            self.project.dataset_id = request.POST.get("dataset")
            messages.success(request, "Datensatz erfolgreich gewählt")
        elif self.step == "architecture":
            post_redirect = self._handle_architecture_form()
        else:
            self.project.name = request.POST.get("name")
            messages.success(request, "Projekteinstellungen gespeichert")

        self.project.save()

        if post_redirect is not None:
            return post_redirect

        return redirect("project-details", self.kwargs["pk"])

    def _setup(self):
        self.step = self._get_step()
        self.project = self._get_project()
        self.context = {"step": self.step, "project": self.project}
        self.context = {**self.context, **self._get_step_data()}

        if self.step == "architecture":
            self.context["layer_list"] = layer_list

            if self.project.architecture is None:
                new_architecture = Architecture()
                new_architecture.save()
                self.project.architecture = new_architecture
                self.project.save()

            self.context["architecture_json"] = json.dumps(
                self.project.architecture.architecture_json
            )
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
            return {"architectures": Architecture.objects.exclude(custom=False)}
        else:
            return {}

    def _handle_architecture_form(self):
        if self.request.POST.get("custom_architecture") is not None:
            custom_architecture = Architecture.objects.get(pk=self.request.POST.get("custom_architecture"))
            self.project.architecture = custom_architecture
            self.project.save()
            messages.success(self.request, "Architektur geladen")

        return redirect("project-edit-architecture", self.kwargs["pk"])

class ProjectDeleteView(DeleteView):
    """Responsible for deleting all the data of a project."""

    model = Project
    success_url = reverse_lazy("project-list")
    template_name = "project/delete_project.html"
