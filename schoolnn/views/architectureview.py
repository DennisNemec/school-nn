import json

from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from schoolnn.models import Architecture
from django.urls import reverse_lazy
from schoolnn.resources.static.layer_list import provided_layer
from schoolnn.views.mixins import (
    AuthenticatedCreateView,
    AuthenticatedQuerysetMixin,
)


class ArchitectureListView(AuthenticatedQuerysetMixin, ListView):
    model = Architecture
    ordering = "-created_at"
    context_object_name = "architectures"
    template_name = "architectures/architecture_overview.html"

    def get_queryset(self):
        return super().get_queryset().filter(name__isnull=False)


class ArchitectureDetailView(AuthenticatedQuerysetMixin, DetailView):
    model = Architecture
    template_name = "architectures/architecture_details.html"


class ArchitectureDeleteView(AuthenticatedQuerysetMixin, DeleteView):
    model = Architecture
    success_url = reverse_lazy("architecture-list")
    template_name = "architectures/delete_architecture.html"


class ArchitectureEditView(AuthenticatedQuerysetMixin, UpdateView):
    model = Architecture
    fields = ["name"]
    template_name = "architectures/edit_architecture.html"


class ArchitectureCreateView(AuthenticatedCreateView):
    model = Architecture
    template_name = "architectures/create_architecture.html"
    fields = ["name"]

    def form_valid(self, form):
        form.instance.custom = True
        return super(ArchitectureCreateView, self).form_valid(form)


class ArchitectureEditorView(AuthenticatedQuerysetMixin, UpdateView):
    model = Architecture
    context_object_name = "architecture"
    template_name = "editor/architecture_editor.html"
    fields = ["architecture_json"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["layer_list"] = json.dumps(provided_layer())
        context["architecture_json"] = json.dumps(
            self.object.architecture_json
        )
        context["selected_dataset_label_count"] = 32  # dummy value

        return context
