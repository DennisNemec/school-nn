from django.urls import path
from .views.architectureview import ArchitectureCreateView, ArchitectureDeleteView, ArchitectureEditView
from .views.architectureview import ArchitectureListView, ArchitectureDetailView
from .views.datasets import DatasetCreate, DatasetList
from .views.datasets import DatasetDetail, DatasetUpdate, DatasetDelete
from .views.images import ImageView
from .views.base_view import BaseView

urlpatterns = [
    path("", BaseView.as_view()),
    path("datasets/", DatasetList.as_view(), name="dataset-list"),
    path("datasets/<int:pk>/", DatasetDetail.as_view(), name="dataset-detail"),
    path("datasets/add/", DatasetCreate.as_view(), name="dataset-add"),
    path(
        "datasets/<int:pk>/edit/", DatasetUpdate.as_view(), name="dataset-edit"
    ),
    path(
        "datasets/<int:pk>/delete/",
        DatasetDelete.as_view(),
        name="dataset-delete",
    ),
    path("images/<int:pk>", ImageView.as_view(), name="image-show"),
    path("architectures/", ArchitectureListView.as_view(), name="architecture-list"),
    path("architectures/<int:pk>/", ArchitectureDetailView.as_view(), name="architecture-detail"),
    path("architectures/<int:pk>/delete/", ArchitectureDeleteView.as_view(), name="architecture-delete"),
    path("architectures/<int:pk>/edit/", ArchitectureEditView.as_view(), name="architecture-edit"),
    path("architectures/add/", ArchitectureCreateView.as_view(), name="architecture-create"),
]
