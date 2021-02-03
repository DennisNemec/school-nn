from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from schoolnn.models import Architecture

class ArchitectureListView(ListView):
    model = Architecture
    template_name = "architecture/list.html"

class ArchitectureDetailView(DetailView):
    model = Architecture
    template_name = "architecture/detail.html"

class ArchitectureDeleteView(DeleteView):
    model = Architecture
    template_name = "architecture/delete.html"

class ArchitectureEditView(UpdateView):
    model = Architecture
    template_name = "architecture/create.html"

class ArchitectureCreateView(CreateView):
    model = Architecture
    template_name = "architecture/create.html"