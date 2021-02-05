from django.urls import path
from schoolnn.views.datasets import DatasetCreate, DatasetList, DatasetDetail
from schoolnn.views.images import ImageView

urlpatterns = [
    path("datasets/", DatasetList.as_view(), name="dataset-list"),
    path("datasets/<int:pk>/", DatasetDetail.as_view(), name="dataset-detail"),
    path("datasets/add/", DatasetCreate.as_view(), name="dataset-add"),
    path("images/<int:pk>", ImageView.as_view(), name="image-show")
]
