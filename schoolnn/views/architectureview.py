import json

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from schoolnn.models import Architecture
from django.urls import reverse_lazy
from schoolnn.resources.static.layer_list import layer_list


class ArchitectureListView(ListView):
    model = Architecture
    context_object_name = "architectures"
    template_name = "architectures/list.html"


class ArchitectureDetailView(DetailView):
    model = Architecture
    template_name = "architectures/detail.html"


class ArchitectureDeleteView(DeleteView):
    model = Architecture
    success_url = reverse_lazy("architecture-list")
    template_name = "architectures/delete.html"


class ArchitectureEditView(UpdateView):
    model = Architecture
    fields = ["name"]
    template_name = "architectures/add.html"


class ArchitectureCreateView(CreateView):
    model = Architecture
    template_name = "architectures/add.html"
    fields = ["name"]


class ArchitectureEditorView(UpdateView):
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
