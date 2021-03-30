"""Contains all HTTP handling having to do with training."""
from django import forms
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from schoolnn.training import (
    TrainingManager,
)
from schoolnn.models import (
    Project,
    TrainingPass,
    LossFunction,
    Optimizer,
)
from schoolnn.views.mixins import UserIsProjectOwnerMixin
from ..architectureview import get_error_message

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
            return redirect("project-edit-parameters", pk=project.id)

        training_pass_count = TrainingPass.objects.filter(
            project=project
        ).count()

        default_name = "Trainingsdurchlauf {}".format(training_pass_count + 1)

        validation_error_message = get_error_message(
            project.architecture.architecture_json,
            arch_name=project.architecture.name,
        )
        if validation_error_message:
            messages.error(self.request, validation_error_message)
            return redirect("show-trainings", project_pk=project_pk)

        context = {
            "project": project,
            "form": TrainingStartForm(initial={"name": default_name}),
        }
        return render(request, self.template_name, context)

    def post(self, request, project_pk: int = 0):
        """Handle committed dataset create form."""
        form = TrainingStartForm(request.POST)
        if form is None:
            raise ValueError("Failed to parse the dataset create form")

        project = Project.objects.get(pk=project_pk)
        validation_error_message = get_error_message(
            project.architecture.architecture_json,
            arch_name=project.architecture.name,
        )
        if validation_error_message:
            messages.error(self.request, validation_error_message)
            # TODO kommentar wieder einfügen
            return redirect("show-trainings", project_pk=project_pk)

        if form.is_valid():
            project = Project.objects.get(pk=project_pk)
            training_pass = self._valid_form_to_training_pass(form, project)

            return redirect(
                "show-training",
                project_pk=project_pk,
                training_pk=training_pass.id,
            )

        return HttpResponse("Error in form.")
