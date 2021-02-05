from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from schoolnn.models import Architecture


class ArchitectureListView(ListView):
    model = Architecture
    context_object_name = "architectures"
    template_name = "architectures/list.html"


class ArchitectureDetailView(DetailView):
    model = Architecture
    template_name = "architectures/detail.html"


class ArchitectureDeleteView(DeleteView):
    model = Architecture
    template_name = "delete.html"


class ArchitectureEditView(UpdateView):
    model = Architecture
    template_name = "create.html"


class ArchitectureCreateView(CreateView):
    model = Architecture
    template_name = "create.html"
