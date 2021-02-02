from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView, DetailView, EditView
from myapp.models import Architecture

class ArchitectureListView(ListView):
    model = Architecutre
    template_name = "architecture/list.html"

class ArchitectureDetailView(DetailView):
    model = Architecture
    template_name = "architecture/detail.html"

class ArchitectureDeleteView(DeleteView):
    model = Architecture
    template_name = "architecture/delete.html"

class ArchitectureEditView(EditView):
    model = Architecture
    template_name = "architecture/edit.html"

class ArchitectureCreateView(CreateView):
    model = Architecture
    template_name = "architecture/create.html"