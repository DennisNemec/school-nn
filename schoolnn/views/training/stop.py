from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from schoolnn.models import (
    Project,
    TrainingPass,
    TrainingPassState,
)


class TrainingStopView(View):
    """Stop a training pass."""

    def get(self, request, project_pk: int = 0, training_pk: int = 0):
        """Ask for stop confirmation."""
        context = {
            "project": Project.objects.get(pk=project_pk),
            "training_pass": TrainingPass.objects.get(pk=training_pk),
        }
        return render(request, "training/stop_training.html", context=context)

    def post(self, request, training_pk: int = 0, **_kwargs):
        """Stop training pass."""
        training_pass = TrainingPass.objects.get(pk=training_pk)
        training_pass.status = TrainingPassState.STOP_REQUESTED.value
        training_pass.save(update_fields=["status"])
        return HttpResponseRedirect("../{}".format(training_pass.id))
