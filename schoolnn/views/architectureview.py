import json

from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from schoolnn.models import Architecture
from django.urls import reverse_lazy
from schoolnn.resources.static.layer_list import layer_list
from schoolnn.views.mixins import (
    AuthenticatedCreateView,
    AuthenticatedQuerysetMixin,
)


class ArchitectureListView(AuthenticatedQuerysetMixin, ListView):
    model = Architecture
    ordering = "-created_at"
    context_object_name = "architectures"
    template_name = "architectures/list.html"


class ArchitectureDetailView(AuthenticatedQuerysetMixin, DetailView):
    model = Architecture
    template_name = "architectures/detail.html"


class ArchitectureDeleteView(AuthenticatedQuerysetMixin, DeleteView):
    model = Architecture
    success_url = reverse_lazy("architecture-list")
    template_name = "architectures/delete.html"


class ArchitectureEditView(AuthenticatedQuerysetMixin, UpdateView):
    model = Architecture
    fields = ["name"]
    template_name = "architectures/edit.html"


class ArchitectureCreateView(AuthenticatedCreateView):
    model = Architecture
    template_name = "architectures/add.html"
    fields = ["name"]

    def form_valid(self, form):
        form.instance.custom = True
        return super(ArchitectureCreateView, self).form_valid(form)


class ArchitectureEditorView(AuthenticatedQuerysetMixin, UpdateView):
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
