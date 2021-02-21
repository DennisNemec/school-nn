import json

from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from schoolnn.models import Architecture
from django.urls import reverse_lazy
from schoolnn.resources.static.layer_list import layer_list
from schoolnn.views.mixins import (
    AuthenticatedCreateView,
    AuthenticatedMultipleObjectMixin,
    AuthenticatedSingleObjectMixin,
)


class ArchitectureListView(ListView, AuthenticatedMultipleObjectMixin):
    model = Architecture
    ordering = "-created_at"
    context_object_name = "architectures"
    template_name = "architectures/list.html"


class ArchitectureDetailView(DetailView, AuthenticatedSingleObjectMixin):
    model = Architecture
    template_name = "architectures/detail.html"


class ArchitectureDeleteView(DeleteView, AuthenticatedSingleObjectMixin):
    model = Architecture
    success_url = reverse_lazy("architecture-list")
    template_name = "architectures/delete.html"


class ArchitectureEditView(UpdateView, AuthenticatedSingleObjectMixin):
    model = Architecture
    fields = ["name"]
    template_name = "architectures/add.html"


class ArchitectureCreateView(AuthenticatedCreateView):
    model = Architecture
    template_name = "architectures/add.html"
    fields = ["name"]


class ArchitectureEditorView(UpdateView, AuthenticatedSingleObjectMixin):
    model = Architecture
    context_object_name = "architecture"
    template_name = "editor/editor.html"
    fields = ["architecture_json"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["layer_list"] = layer_list
        context["architecture_json"] = json.dumps(
            self.object.architecture_json
        )

        return context
