from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from schoolnn.models import (
    Project,
    TrainingPass,
)
from schoolnn.views.mixins import UserIsProjectOwnerMixin
from schoolnn.training.training_management import TrainingManager


class TrainingContinueView(UserIsProjectOwnerMixin, View):
    """Continue a training pass."""

    def get(self, request, project_pk: int = 0, training_pk: int = 0):
        """Ask for stop confirmation."""
        context = {
            "project": Project.objects.get(pk=project_pk),
            "training_pass": TrainingPass.objects.get(pk=training_pk),
        }
        return render(
            request,
            "training/continue_training.html",
            context=context,
        )

    def post(self, request, training_pk: int = 0, **_kwargs):
        """Continue training pass."""
        training_pass = TrainingPass.objects.get(pk=training_pk)
        training_manager = TrainingManager()
        training_manager.continue_training_pass(training_pass)
        return HttpResponseRedirect("../{}".format(training_pass.id))
