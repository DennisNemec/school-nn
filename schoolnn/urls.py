from django.urls import path
from schoolnn.views.architectureview import ArchitectureListView, ArchitectureDetailView, ArchitectureDeleteView, ArchitectureEditView, ArchitectureCreateView

urlpatterns = [
    path("architectures/", ArchitectureListView.as_view(), name="architecture-list"),
    path("architectures/architecture", ArchitectureDetailView.as_view(), name="architecture-create"),
    path("architecture/architecture/delete", ArchitectureDeleteView.as_view(), name="architecture-delete"),
    path("architecture/architecture/edit", ArchitectureEditView.as_view(), name="architecture-edit"),
    path("architecture/architecture/create", ArchitectureCreateView.as_view(), name="architecture-create"),
]