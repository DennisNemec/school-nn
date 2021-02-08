from django.urls import path
from .views.architectureview import ArchitectureCreateView, ArchitectureDeleteView, ArchitectureEditView
from .views.architectureview import ArchitectureListView, ArchitectureDetailView

urlpatterns = [
    path("architectures/", ArchitectureListView.as_view(), name="architecture-list"),
    path("architectures/<int:pk>/", ArchitectureDetailView.as_view(), name="architecture-detail"),
    path("architectures/<int:pk>/delete", ArchitectureDeleteView.as_view(), name="architecture-delete"),
    path("architectures/<int:pk>/edit", ArchitectureEditView.as_view(), name="architecture-edit"),
    path("architectures/add", ArchitectureCreateView.as_view(), name="architecture-create"),
]
