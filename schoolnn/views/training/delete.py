from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from schoolnn.models import (
    Project,
    TrainingPass,
)
from schoolnn.views.mixins import UserIsProjectOwnerMixin


class TrainingDeleteView(UserIsProjectOwnerMixin, View):
    """Delete a training pass."""

    def get(self, request, project_pk: int = 0, training_pk: int = 0):
        """Ask for deletion confirmation."""
        context = {
            "project": Project.objects.get(pk=project_pk),
            "training_pass": TrainingPass.objects.get(pk=training_pk),
        }
        return render(
            request, "training/delete_training.html", context=context
        )

    def post(self, request, training_pk: int = 0, **_kwargs):
        """Delete training pass."""
        TrainingPass.objects.get(pk=training_pk).delete()
        HttpResponseRedirect("../create")
