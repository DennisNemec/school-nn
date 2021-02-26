import json
from typing import Optional

from django import forms
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, resolve
from django.views import View
from django.views.generic import DetailView, CreateView, ListView, DeleteView

from schoolnn.models import (
    Project,
    Dataset,
    Architecture,
    TrainingParameter,
    LossFunction,
    Optimizer,
    AugmentationOptions,
    TerminationCondition,
)
from schoolnn.resources.static.layer_list import layer_list
from schoolnn.views.mixins import (
    LoginRequiredMixin,
    AuthenticatedQuerysetMixin,
)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Responsible for the creation of projects."""

    class ProjectCreateForm(forms.ModelForm):
        class Meta:
            fields = ["name"]
            model = Project

    form_class = ProjectCreateForm
    template_name = "project/create_project.html"

    object: Optional[Project] = None

    def form_valid(self, form: ProjectCreateForm):
        """If the form is valid, save the associated model."""

        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()

            if self.object is None:
                # TODO: Translation für Fehlermeldung
                raise ValueError("Failed to parse the project create form")

            # Create and assign anonymous architecture
            new_architecture = Architecture(user=self.request.user)
            new_architecture.save()

            self.object.architecture = new_architecture
            self.object.save()

        messages.success(
            self.request, f"Projekt „{self.object.name}“ erfolgreich erstellt."
        )

        return HttpResponseRedirect(self.get_success_url())


class ProjectListView(AuthenticatedQuerysetMixin, ListView):
    """Responsible for listing all projects."""

    queryset = Project.objects.order_by("-created_at")
    context_object_name = "projects"
    template_name = "project/project_overview.html"


class ProjectDetailView(AuthenticatedQuerysetMixin, DetailView):
    """Responsible for displaying a single project."""

    model = Project
    template_name = "project/project_details.html"


class ProjectEditView(LoginRequiredMixin, View):
    """Responsible for editing all the data of a project."""

    template_name: str = "project/edit_project.html"
    valid_steps: list = [
        "settings",
        "dataset",
        "architecture",
        "load_architecture",
        "parameters",
    ]

    def get(self, request, *args, **kwargs):
        error_redirect = self._check_and_setup()

        if error_redirect is not None:
            return error_redirect

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        error_redirect = self._check_and_setup()

        if error_redirect is not None:
            return error_redirect

        if self.step == "settings":
            post_redirect = self._handle_settings_form()
        elif self.step == "dataset":
            post_redirect = self._handle_dataset_load_form()
        elif self.step == "load_architecture":
            post_redirect = self._handle_architecture_load_form()
        elif self.step == "architecture":
            post_redirect = self._handle_architecture_form()
        elif self.step == "parameters":
            post_redirect = self._handle_parameters_form()
        else:
            messages.error(self.request, "Invalider Projekt-Editier-Schritt.")
            post_redirect = self.default_redirect

        self.project.save()

        return post_redirect

    def _check_and_setup(self):
        try:
            self.project = self._get_project()
        except Project.DoesNotExist:
            messages.error(self.request, "Dieses Projekt existiert nicht.")
            return redirect("project-list")

        if self.project.user != self.request.user:
            messages.error(self.request, "Zugriff verweigert.")
            return redirect("project-list")

        self.default_redirect = redirect("project-details", self.kwargs["pk"])
        self.step = self._get_step()
        self.project = self._get_project()
        self._ensure_architecture_exists()
        self._set_context()

        return None

    # project-edit-dataset -> dataset
    def _get_step(self):
        url_name = resolve(self.request.path_info).url_name
        step = url_name.split("-")[-1]

        if step not in self.valid_steps:
            raise ValueError("Invalid project edit step.")

        return step

    def _get_project(self):
        return Project.objects.get(pk=self.kwargs["pk"])

    def _set_context(self):
        self.context = {"step": self.step, "project": self.project}
        self.context = {**self.context, **self._get_step_context()}

    def _get_step_context(self):
        if self.step == "dataset":
            return {"datasets": self._get_user_datasets()}
        elif self.step == "architecture":
            return {
                "layer_list": layer_list,
                "architecture_json": json.dumps(
                    self.project.architecture.architecture_json
                ),
            }
        elif self.step == "load_architecture":
            return {"architectures": self._get_user_architectures()}
        elif self.step == "parameters":
            parameters = TrainingParameter.from_dict(
                self.project.training_parameter_json
            )

            return {
                "parameters": parameters,
                "parameter_form": TrainingParameterForm(
                    initial={
                        "validation_split": parameters.validation_split,
                        "learning_rate": parameters.learning_rate,
                        "termination_condition_seconds": parameters.termination_condition.seconds,  # noqa: E501
                        "termination_condition_epochs": parameters.termination_condition.epochs,  # noqa: E501
                        "batch_size": parameters.batch_size,
                        "loss_function": parameters.loss_function.value,
                        "optimizer": parameters.optimizer.value,
                        "augmentation_channel_shuffle": parameters.augmentation_options.channel_shuffle,  # noqa: E501
                        "augmentation_brightness": parameters.augmentation_options.brightness,  # noqa: E501
                        "augmentation_gaussian_noise": parameters.augmentation_options.gaussian_noise,  # noqa: E501
                        "augmentation_dropout_boxes": parameters.augmentation_options.dropout_boxes,  # noqa: E501
                        "augmentation_salt_and_pepper": parameters.augmentation_options.salt_and_pepper,  # noqa: E501
                        "augmentation_jpeg_artifacts": parameters.augmentation_options.jpeg_artifacts,  # noqa: E501
                        "augmentation_vertical_flip": parameters.augmentation_options.vertical_flip,  # noqa: E501
                        "augmentation_distortion": parameters.augmentation_options.distortion,  # noqa: E501
                        "augmentation_rotate": parameters.augmentation_options.rotate,  # noqa: E501
                        "augmentation_scale_and_translate": parameters.augmentation_options.scale_and_translate,  # noqa: E501
                        "augmentation_color": parameters.augmentation_options.color,  # noqa: E501
                    }
                ),
            }
        else:
            return {}

    #
    def _get_user_datasets(self):
        return Dataset.objects.filter(user=self.request.user)

    #
    def _get_user_architectures(self):
        return Architecture.objects.filter(user=self.request.user).exclude(
            name__isnull=True
        )

    #
    def _handle_settings_form(self):
        name = self.request.POST.get("name", None)

        if name is None:
            messages.error(self.request, "Projektname nicht angegeben.")
            return self.default_redirect

        self.project.name = name
        messages.success(self.request, "Projekteinstellungen gespeichert.")

        return self.default_redirect

    #
    def _handle_dataset_load_form(self):
        dataset_id = self.request.POST.get("dataset", None)

        if dataset_id is None:
            raise ValueError("Datensatz-ID nicht angegeben.")

        dataset = Dataset.objects.filter(pk=dataset_id).first()

        if dataset is None:
            messages.error(
                self.request,
                "Der gewählte Datensatz konnte nicht gefunden werden.",
            )
            return self.default_redirect

        self.project.dataset = dataset
        messages.success(
            self.request, f"Datensatz „{dataset.name}“ erfolgreich gewählt."
        )

        return self.default_redirect

    #
    def _handle_architecture_form(self):
        architecture_json = self.request.POST.get("architecture_json", None)

        if architecture_json is None:
            raise ValueError("Architektur-JSON nicht angegeben.")

        # Todo: Check if json is valid
        self.project.architecture.architecture_json = json.loads(
            architecture_json
        )
        self.project.architecture.save()

        messages.success(
            self.request, "Die Änderungen wurden erfolgreich gespeichert."
        )

        return redirect("project-edit-architecture", self.kwargs["pk"])

    #
    def _handle_architecture_load_form(self):
        architecture_id = self.request.POST.get("custom_architecture", None)

        if architecture_id is None:
            raise ValueError("Architektur-ID nicht angegeben.")

        loaded_architecture = Architecture.objects.filter(
            pk=architecture_id
        ).first()

        if loaded_architecture is None:
            messages.error(
                self.request,
                "Die gewählte Architektur konnte nicht gefunden werden.",
            )
            return redirect("project-edit-architecture", self.kwargs["pk"])

        # Set Architecture JSON
        self.project.architecture.architecture_json = (
            loaded_architecture.architecture_json
        )
        self.project.architecture.save()

        messages.success(
            self.request,
            f"Architektur „{loaded_architecture.name}“ erfolgreich geladen.",
        )

        return redirect("project-edit-architecture", self.kwargs["pk"])

    def _handle_parameters_form(self):
        form = TrainingParameterForm(self.request.POST)

        if not form.is_valid():
            messages.error(
                self.request,
                "Parameter nicht valide.",
            )

            return redirect("project-details", self.kwargs["pk"])

        termination_condition = TerminationCondition.from_dict(
            {
                "seconds": form.cleaned_data["termination_condition_seconds"],
                "epochs": form.cleaned_data["termination_condition_epochs"],
            }
        )
        loss_function = LossFunction(form.cleaned_data["loss_function"])
        optimizer = Optimizer(form.cleaned_data["optimizer"])
        augmentation_options = AugmentationOptions.from_dict(
            {
                "channel_shuffle": form.cleaned_data[
                    "augmentation_channel_shuffle"
                ],
                "brightness": form.cleaned_data["augmentation_brightness"],
                "gaussian_noise": form.cleaned_data[
                    "augmentation_gaussian_noise"
                ],
                "dropout_boxes": form.cleaned_data[
                    "augmentation_dropout_boxes"
                ],
                "salt_and_pepper": form.cleaned_data[
                    "augmentation_salt_and_pepper"
                ],
                "jpeg_artifacts": form.cleaned_data[
                    "augmentation_jpeg_artifacts"
                ],
                "vertical_flip": form.cleaned_data[
                    "augmentation_vertical_flip"
                ],
                "distortion": form.cleaned_data["augmentation_distortion"],
                "rotate": form.cleaned_data["augmentation_rotate"],
                "scale_and_translate": form.cleaned_data[
                    "augmentation_scale_and_translate"
                ],
                "color": form.cleaned_data["augmentation_color"],
            }
        )

        new_parameters = TrainingParameter(
            validation_split=form.cleaned_data["validation_split"],
            learning_rate=form.cleaned_data["learning_rate"],
            termination_condition=termination_condition,
            batch_size=form.cleaned_data["batch_size"],
            loss_function=loss_function,
            optimizer=optimizer,
            augmentation_options=augmentation_options,
        )

        self.project.training_parameter_json = new_parameters.to_dict()

        messages.success(
            self.request, "Die Änderungen wurden erfolgreich gespeichert."
        )

        return redirect("project-edit-parameters", self.kwargs["pk"])

    def _ensure_architecture_exists(self):
        if self.project.architecture is None:
            # Create and assign anonymous architecture
            new_architecture = Architecture(user=self.request.user)
            new_architecture.save()

            self.project.architecture = new_architecture
            self.project.save()


class TrainingParameterForm(forms.Form):
    fieldsets = [
        {
            "headline": "Allgemeine Einstellungen",
            "fields": [
                "validation_split",
                "learning_rate",
                "batch_size",
                "loss_function",
                "optimizer",
            ],
            "id": "general_settings",
        },
        {
            "headline": "Abbruchbedingungen",
            "fields": [
                "termination_condition_seconds",
                "termination_condition_epochs",
            ],
            "id": "termination_settings",
        },
        {
            "headline": "Augmentierungs-Einstellungen",
            "fields": [
                "augmentation_channel_shuffle",
                "augmentation_brightness",
                "augmentation_gaussian_noise",
                "augmentation_dropout_boxes",
                "augmentation_salt_and_pepper",
                "augmentation_jpeg_artifacts",
                "augmentation_vertical_flip",
                "augmentation_distortion",
                "augmentation_rotate",
                "augmentation_scale_and_translate",
                "augmentation_color",
            ],
            "id": "augmentation_settings",
        },
    ]

    validation_split = forms.FloatField(
        label="Validierungs-Anteil",
        min_value=0.0,
        max_value=0.5,
        # widget=NumberInput(attrs={
        #     "type": "range",
        #     "oninput": "updateTextInput(this.value);"
        # })
    )

    learning_rate = forms.FloatField(
        label="Lernrate", min_value=0.001, max_value=0.2
    )

    termination_condition_seconds = forms.IntegerField(
        label="Vergangene Sekunden seit Trainingsbeginn",
        min_value=1,
        max_value=86400,
    )

    termination_condition_epochs = forms.IntegerField(
        label="Anzahl der Epochen", min_value=1, max_value=128
    )

    batch_size = forms.IntegerField(
        label="Batchgröße", min_value=1, max_value=128
    )

    # Todo: Build choices by calling LossFunction.to_array()
    loss_function = forms.ChoiceField(
        label="Loss-Funktion",
        choices=[("categorical_crossentropy", "Categorical Crossentropy")],
    )

    # Todo: Build choices by calling Optimizer.to_array()
    optimizer = forms.ChoiceField(
        label="Optimierer",
        choices=[
            ("sgd", "Stochastic Gradient Descent"),
            ("rmsprop", "RMSprop"),
            ("adam", "Adam"),
            ("nadam", "NAdam"),
            ("adadelta", "Adadelta"),
            ("adamax", "Adamax"),
        ],
    )

    augmentation_channel_shuffle = forms.BooleanField(
        label="Channel-Shuffle", required=False
    )

    augmentation_brightness = forms.BooleanField(
        label="Helligkeit", required=False
    )

    augmentation_gaussian_noise = forms.BooleanField(
        label="Gaußsches Rauschen", required=False
    )

    augmentation_dropout_boxes = forms.BooleanField(
        label="Dropout-Boxen", required=False
    )

    augmentation_salt_and_pepper = forms.BooleanField(
        label="Salz und Pfeffer", required=False
    )

    augmentation_jpeg_artifacts = forms.BooleanField(
        label="JPEG-Artefakte", required=False
    )

    augmentation_vertical_flip = forms.BooleanField(
        label="Vertikale Spiegelung", required=False
    )

    augmentation_distortion = forms.BooleanField(
        label="Verzerrung", required=False
    )

    augmentation_rotate = forms.BooleanField(label="Rotation", required=False)

    augmentation_scale_and_translate = forms.BooleanField(
        label="Skalierung und Verschiebung", required=False
    )

    augmentation_color = forms.BooleanField(label="Farbe", required=False)


class ProjectDeleteView(AuthenticatedQuerysetMixin, DeleteView):
    """Responsible for deleting all the data of a project."""

    model = Project
    success_url = reverse_lazy("project-list")
    template_name = "project/delete_project.html"

    def delete(self, request, *args, **kwargs):
        project = self.get_object()

        if project.architecture is not None:
            project.architecture.delete()

        messages.success(
            self.request, f"Projekt „{project.name}“ erfolgreich gelöscht."
        )

        project.delete()

        return HttpResponseRedirect(self.success_url)
