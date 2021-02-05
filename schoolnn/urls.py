# flake8: noqa

from django.urls import path
from schoolnn.views.datasets import DatasetCreate, DatasetList, DatasetDetail, DatasetUpdate, DatasetDelete
from schoolnn.views.images import ImageView

urlpatterns = [
    path("datasets/", DatasetList.as_view(), name="dataset-list"),
    path("datasets/<int:pk>/", DatasetDetail.as_view(), name="dataset-detail"),
    path("datasets/add/", DatasetCreate.as_view(), name="dataset-add"),
    path("datasets/<int:pk>/edit/", DatasetUpdate.as_view(), name="dataset-edit"),
    path("datasets/<int:pk>/delete/", DatasetDelete.as_view(), name="dataset-delete"),
    path("images/<int:pk>", ImageView.as_view(), name="image-show")
]
