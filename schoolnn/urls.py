"""Manages URL routing of the webapp."""

from django.urls import path
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
]
