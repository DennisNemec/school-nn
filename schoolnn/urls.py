from django.urls import path
from schoolnn.views.architectureview import ArchitectureListView, ArchitectureDetailView, ArchitectureDeleteView, ArchitectureEditView, ArchitectureCreateView

urlpatterns = [
    path("architectures/", ArchitectureListView.as_view(), name="architecture-list"),
    path("architectures/architecture", ArchitectureDetailView.as_view(), name="architecture-create"),
    path("architectures/architecture/delete", ArchitectureDeleteView.as_view(), name="architecture-delete"),
    path("architectures/architecture/edit", ArchitectureEditView.as_view(), name="architecture-edit"),
    path("architectures/architecture/create", ArchitectureCreateView.as_view(), name="architecture-create"),
]