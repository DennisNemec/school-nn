"""Contains all HTTP handling having to do with training."""
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.shortcuts import render
from schoolnn.training import TrainingManager
from schoolnn.models import (
    Project,
    TrainingPass,
    LossFunction,
    Optimizer,
)
from schoolnn.views.mixins import UserIsProjectOwnerMixin

_LOSS_CHOICES = [
    (LossFunction.CATEGORICAL_CROSSENTROPY.value, "Categorical Crossentropy"),
]

_OPTIMIZER_CHOICES = [
    (Optimizer.ADAM.value, "Adam"),
    (Optimizer.RMSPROP.value, "RMSprop"),
    (Optimizer.SGD.value, "SGD"),
    (Optimizer.NADAM.value, "Nadam"),
    (Optimizer.ADADELTA.value, "Adadelta"),
    (Optimizer.ADAMAX.value, "Adamax"),
]


class TrainingStartForm(forms.Form):
    """Dataset form that contains an additional file field."""

    name = forms.CharField()


class TrainingCreateView(UserIsProjectOwnerMixin, View):
    """Handle creation of datasets."""

    template_name = "training/create_training.html"

    def _valid_form_to_training_pass(
        self,
        form: forms.Form,
        project: Project,
    ) -> TrainingPass:
        training_manager = TrainingManager()
        training_pass = training_manager.apply_job(
            project,
            form.cleaned_data["name"],
        )
        return training_pass

    def get(self, request, project_pk: int = 0):
        """Get site to start a new training pass."""
        project = Project.objects.get(pk=project_pk)
        if project.training_parameter is None:
            return HttpResponseRedirect("../edit/parameters")
        context = {
            "project": project,
            "form": TrainingStartForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request, project_pk: int = 0):
        """Handle committed dataset create form."""
        form = TrainingStartForm(request.POST)
        if form is None:
            raise ValueError("Failed to parse the dataset create form")

        if form.is_valid():
            project = Project.objects.get(pk=project_pk)
            training_pass = self._valid_form_to_training_pass(form, project)

            return HttpResponseRedirect("{}".format(training_pass.id))

        return HttpResponse("Error in form.")
