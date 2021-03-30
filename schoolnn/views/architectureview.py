import json
from typing import Optional, List

from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from schoolnn.training import (
    validate_architecture_json_representation,
    ArchitectureValidationError,
)
from schoolnn.models import Architecture
from schoolnn.resources.static.layer_list import provided_layer
from schoolnn.views.mixins import (
    AuthenticatedCreateView,
    AuthenticatedQuerysetMixin,
)


def get_error_message(
    architecture_json: List[dict],
    arch_name: Optional[str] = None,
) -> Optional[str]:
    validation_err = validate_architecture_json_representation(
        architecture_json
    )

    # Generate message text
    if arch_name:
        message_error_prefix = (
            "Architektur „{}“ ist ungültig und muss "
            "nochmal bearbeitet werden.\n".format(arch_name)
        )
    else:
        message_error_prefix = (
            "Die Architektur ist ungültig und muss "
            "nochmal bearbeitet werden.\n"
        )
    AVE = ArchitectureValidationError
    if validation_err == AVE.TOO_MANY_CONVOLUTIONS:
        return message_error_prefix + (
            "Die Zusammenfaltungen würden eine negative Dimension " "ergeben."
        )
    elif validation_err == AVE.INPUT_SHAPE_NOT_RGB:
        return message_error_prefix + (
            "Die Eingabedimension muss NxNx3 sein, für jeden RGB Kanal."
        )
    elif validation_err == AVE.INPUT_SHAPE_NOT_3D:
        return message_error_prefix + (
            "Die Eingabedimension muss 3D sein. \n"
            "Höhe x Breite x 3 (für RGB-Kanäle)"
        )
    elif validation_err == AVE.INPUT_SHAPE_NOT_SQUARE:
        return message_error_prefix + (
            "Es werden nur quadratische Bilder untersützt.\n"
            "Die Eingabedimension muss NxNx3 sein."
        )
    elif validation_err == AVE.NULL_VALUE:
        return message_error_prefix + (
            "Bitte überprüfe, ob noch Werte auf Null gesetzt sind."
        )
    elif validation_err == AVE.UNKNOWN:
        return message_error_prefix

    return None


class ArchitectureListView(AuthenticatedQuerysetMixin, ListView):
    model = Architecture
    ordering = "-created_at"
    context_object_name = "architectures"
    template_name = "architectures/architecture_overview.html"

    def get_queryset(self):
        return super().get_queryset().filter(name__isnull=False)


class ArchitectureDetailView(AuthenticatedQuerysetMixin, DetailView):
    model = Architecture
    template_name = "architectures/architecture_details.html"


class ArchitectureDeleteView(AuthenticatedQuerysetMixin, DeleteView):
    model = Architecture
    success_url = reverse_lazy("architecture-list")
    template_name = "architectures/delete_architecture.html"

    def delete(self, request, *args, **kwargs):
        architecture = self.get_object()

        messages.success(
            self.request,
            f"Architektur „{architecture.name}“ erfolgreich gelöscht.",
        )

        architecture.delete()

        return HttpResponseRedirect(self.success_url)


class ArchitectureEditView(AuthenticatedQuerysetMixin, UpdateView):
    model = Architecture
    fields = ["name"]
    template_name = "architectures/edit_architecture.html"

    def form_valid(self, form):
        architecture = form.instance

        error_message = get_error_message(
            architecture_json=architecture.architecture_json,
            arch_name=architecture.name,
        )

        if error_message:
            messages.error(self.request, error_message)
        else:
            msg = "Architektur „{}“ erfolgreich gesetzt.".format(
                architecture.name
            )
            messages.success(self.request, msg)

        return super(ArchitectureEditView, self).form_valid(form)


class ArchitectureCreateView(AuthenticatedCreateView):
    model = Architecture
    template_name = "architectures/create_architecture.html"
    fields = ["name"]

    def form_valid(self, form):
        architecture = form.instance

        error_message = get_error_message(
            architecture_json=architecture.architecture_json,
            arch_name=architecture.name,
        )

        if error_message:
            messages.error(self.request, error_message)
        else:
            msg = "Architektur „{}“ erfolgreich gesetzt.".format(
                architecture.name
            )
            messages.success(self.request, msg)

        form.instance.custom = True
        return super(ArchitectureCreateView, self).form_valid(form)


class ArchitectureEditorView(AuthenticatedQuerysetMixin, UpdateView):
    model = Architecture
    context_object_name = "architecture"
    template_name = "editor/architecture_editor.html"
    fields = ["architecture_json"]

    def form_valid(self, form):
        architecture = form.instance

        error_message = get_error_message(
            architecture_json=architecture.architecture_json,
            arch_name=architecture.name,
        )
        if error_message:
            messages.error(self.request, error_message)
        else:
            msg = "Architektur „{}“ erfolgreich gesetzt.".format(
                architecture.name
            )
            messages.success(self.request, msg)

        return super(ArchitectureEditorView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["layer_list"] = json.dumps(provided_layer())
        context["architecture_json"] = json.dumps(
            self.object.architecture_json
        )
        context["selected_dataset_label_count"] = 32  # dummy value

        return context
