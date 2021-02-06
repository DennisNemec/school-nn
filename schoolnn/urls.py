"""The SchoolNN URLs."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.base_view.BaseView.as_view()),
]
