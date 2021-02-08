from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from schoolnn.models import Architecture
from django.urls import reverse_lazy



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
    template_name = "architectures/edit.html"


class ArchitectureCreateView(CreateView):
    model = Architecture
    template_name = "architectures/add.html"
    fields = '__all__'
