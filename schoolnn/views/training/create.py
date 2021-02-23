"""Contains all HTTP handling having to do with training."""
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.shortcuts import render
from schoolnn.training import TrainingManager
from schoolnn.models import (
    AugmentationOptions,
    Project,
    TrainingParameter,
    TrainingPass,
    LossFunction,
    Optimizer,
    TerminationCondition,
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
    learning_rate = forms.FloatField(
        max_value=0.5, min_value=0.00001, initial=0.01
    )
    batch_size = forms.IntegerField(min_value=1, max_value=4096, initial=32)
    validation_split = forms.FloatField(
        min_value=0.0, max_value=0.5, initial=0.1
    )
    loss_function = forms.ChoiceField(choices=_LOSS_CHOICES)
    optimizer = forms.ChoiceField(choices=_OPTIMIZER_CHOICES)

    terminate_if_validation_loss_rises = forms.BooleanField(
        label="Stop if validation loss rises", required=False
    )
    terminate_after_epochs = forms.IntegerField(
        max_value=1000, min_value=1, initial=16, label="Maximum epochs"
    )
    terminate_after_minutes = forms.IntegerField(
        min_value=1, initial=120, label="Maximum runtime in minutes"
    )

    augmentation_channel_shuffle = forms.BooleanField(
        required=False, label="Channel shuffle", initial=True
    )
    augmentation_brightness = forms.BooleanField(
        required=False, label="Brightness", initial=True
    )
    augmentation_gaussian_noise = forms.BooleanField(
        required=False, label="Gaussian noise", initial=True
    )
    augmentation_dropout_boxes = forms.BooleanField(
        required=False, label="Dropout Boxes", initial=True
    )
    augmentation_salt_and_pepper = forms.BooleanField(
        required=False, label="Salt and pepper", initial=True
    )
    augmentation_jpeg_artifacts = forms.BooleanField(
        required=False, label="JPEG Artifacts", initial=True
    )
    augmentation_gaussian_blur = forms.BooleanField(
        required=False, label="Gaussian Blur", initial=True
    )
    augmentation_vertical_flip = forms.BooleanField(
        required=False, label="Vertical flip", initial=True
    )
    augmentation_distortion = forms.BooleanField(
        required=False, label="Distortion", initial=True
    )
    augmentation_rotate = forms.BooleanField(
        required=False, label="Rotate", initial=True
    )
    augmentation_scale_and_translate = forms.BooleanField(
        required=False, label="Scale and Translate", initial=True
    )
    augmentation_color = forms.BooleanField(
        required=False, label="Color", initial=True
    )


class TrainingCreateView(UserIsProjectOwnerMixin, View):
    """Handle creation of datasets."""

    template_name = "training/create_training.html"

    def _valid_form_to_training_pass(
        self,
        form: forms.Form,
        project: Project,
    ) -> TrainingPass:
        termination_condition = TerminationCondition(
            seconds=form.cleaned_data["terminate_after_minutes"] * 60,
            epochs=form.cleaned_data["terminate_after_epochs"],
            validation_loss_raising=(
                form.cleaned_data["terminate_if_validation_loss_rises"]
            ),
        )

        augmentation_options = AugmentationOptions(
            channel_shuffle=form.cleaned_data["augmentation_channel_shuffle"],
            brightness=form.cleaned_data["augmentation_brightness"],
            gaussian_noise=form.cleaned_data["augmentation_gaussian_noise"],
            dropout_boxes=form.cleaned_data["augmentation_dropout_boxes"],
            salt_and_pepper=form.cleaned_data["augmentation_salt_and_pepper"],
            jpeg_artifacts=form.cleaned_data["augmentation_jpeg_artifacts"],
            gaussian_blur=form.cleaned_data["augmentation_gaussian_blur"],
            vertical_flip=form.cleaned_data["augmentation_vertical_flip"],
            distortion=form.cleaned_data["augmentation_distortion"],
            rotate=form.cleaned_data["augmentation_rotate"],
            scale_and_translate=form.cleaned_data[
                "augmentation_scale_and_translate"
            ],
            color=form.cleaned_data["augmentation_color"],
        )

        training_parameter = TrainingParameter(
            validation_split=form.cleaned_data["validation_split"],
            learning_rate=form.cleaned_data["learning_rate"],
            termination_condition=termination_condition,
            batch_size=form.cleaned_data["batch_size"],
            loss_function=LossFunction(form.cleaned_data["loss_function"]),
            optimizer=Optimizer(form.cleaned_data["optimizer"]),
            augmentation_options=augmentation_options,
        )

        project.training_parameter = training_parameter
        project.save(update_fields=["training_parameter_json"])
        training_manager = TrainingManager()
        training_pass = training_manager.apply_job(project)
        return training_pass

    def get(self, request, project_pk: int = 0):
        """Get site to start a new training pass."""
        context = {
            "project": Project.objects.get(pk=project_pk),
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
