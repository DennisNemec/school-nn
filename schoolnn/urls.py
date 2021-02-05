from django.urls import path
from schoolnn.views.architectureview import ArchitectureListView, ArchitectureDetailView, ArchitectureDeleteView, ArchitectureEditView, ArchitectureCreateView

urlpatterns = [
    path("architectures/", ArchitectureListView.as_view(), name="architecture-list"),
    path("architectures/<int:pk>/", ArchitectureDetailView.as_view(), name="architecture-detail"),
    path("architectures/delete", ArchitectureDeleteView.as_view(), name="architecture-delete"),
    path("architectures/<int:pk>/edit", ArchitectureEditView.as_view(), name="architecture-edit"),
    path("architectures/add", ArchitectureCreateView.as_view(), name="architecture-create"),
]