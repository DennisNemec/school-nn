"""Contains all HTTP handling having to do with datasets."""
import shutil
import json
from typing import Optional
from io import BytesIO

from django.contrib import messages
from django import forms
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.http import HttpResponseRedirect
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView
from schoolnn.dataset import zip_to_full_dataset
from schoolnn.models import Dataset, Label, Image
from schoolnn.views.mixins import (
    LoginRequiredMixin,
    AuthenticatedQuerysetMixin,
)

from .widgets import ImageCheckboxWidget


class DatasetCreateForm(forms.ModelForm):
    """Dataset form that contains an additional file field."""

    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["zip"])]
    )

    class Meta:
        """Django meta information."""

        fields = ["file", "name"]
        model = Dataset


class DatasetClassifyForm(forms.Form):
    """Dataset form that contains an additional file field."""

    image_id_list = forms.ModelMultipleChoiceField(
        queryset=Image.objects.filter(label__isnull=True),
        widget=ImageCheckboxWidget,
        label="",
    )


class DatasetList(AuthenticatedQuerysetMixin, ListView):
    """Lists datasets."""

    model = Dataset
    ordering = "-created_at"
    context_object_name = "datasets"
    template_name = "datasets/dataset_overview.html"

    def get_label_of_datasets(self, dataset):
        """ Extract labels of a dataset. """

        return Label.objects.filter(dataset=dataset).order_by("name")

    def get_images_of_label(self, label, dataset):
        """ Extract images of a given label. """

        return [
            i[0]
            for i in Image.objects.filter(
                label=label, dataset=dataset
            ).values_list("id")
        ]

    def get_queryset(self):
        """ Create queryset for dataset list. """

        listing_type = ""
        datasets = None
        dataset_list = []

        if "type" in self.request.GET:
            listing_type = self.request.GET["type"]

        # check url location
        if listing_type == "own" or listing_type == "":
            datasets = Dataset.objects.order_by("-created_at")
        elif listing_type == "shared":
            datasets = []  # TODO: add shared functionality
        else:
            raise Http404

        for dataset in datasets:
            labels = self.get_label_of_datasets(dataset)

            unlabeled_count = Image.objects.filter(
                dataset=dataset, label__isnull=True
            ).count()

            # save dataset specific details to dataset object
            dataset_dict = {}
            dataset_dict["name"] = dataset.name
            dataset_dict["id"] = dataset.id
            dataset_dict["image_amount"] = 0
            dataset_dict["status"] = {
                "is_completely_labeled": unlabeled_count,
                # TODO: add locale
                "text": "Vollständig" if unlabeled_count == 0 else "In Arbeit",
            }
            dataset_dict["created_at"] = dataset.created_at.strftime(
                "%d.%m.%Y um %H:%M Uhr"
            )

            label_list = []
            for label in labels:
                label_dict = {}
                image_ids = self.get_images_of_label(label, dataset)

                # save label specific details in label object
                # TODO: add locale
                label_dict["name"] = "Klasse: " + label.name
                label_dict["image_ids"] = image_ids[:19]
                label_list.append(label_dict)

                dataset_dict["image_amount"] += len(image_ids)

            dataset_dict["label"] = label_list
            dataset_dict["label_amount"] = len(label_list)

            dataset_list.append(dataset_dict)

        return [listing_type, json.dumps(dataset_list)]


class DatasetDetail(AuthenticatedQuerysetMixin, DetailView):
    """Show dataset details."""

    model = Dataset
    template_name = "datasets/dataset_details.html"

    def get_unlabeled_count(self):
        """
        Returns the amount of unclassified images of \
        a specific dataset.
        """

        return (
            Dataset.objects.get(id=self.kwargs["pk"])
            .image_set.filter(label__isnull=True)
            .count()
        )

    def get_unlabeled_images(self):
        """
        Returns the unclassified images of a specific dataset \
        as an Image object.
        """

        return Dataset.objects.get(id=self.kwargs["pk"]).image_set.filter(
            label__isnull=True
        )

    def get_context_data(self, **kwargs):
        """
        Sets needed context data for use within the template.
        """

        context = super().get_context_data(**kwargs)

        context["unlabeled_count"] = self.get_unlabeled_count()
        context["unlabeled_images"] = self.get_unlabeled_images()

        return context


class DatasetCreate(LoginRequiredMixin, CreateView):
    """Handles creation of datasets."""

    form_class = DatasetCreateForm
    template_name = "datasets/create_dataset.html"

    object: Optional[Dataset] = None

    def form_invalid(self, form):
        raise ValueError("Failed to parse the dataset create form")

    def form_valid(self, form: DatasetCreateForm):
        """Handle committed dataset create form."""
        form.instance.user = self.request.user
        self.object = form.save()

        if self.object is None:
            raise ValueError("Failed to parse the dataset create form")

        self.handle_upload(self.request.FILES["file"])

        messages.success(self.request, "Datensatz erfolgreich erstellt.")

        return HttpResponseRedirect(self.get_success_url())

    def handle_upload(self, zip_binary):
        """Unzip uploaded file to storage."""
        zip_in_ram = BytesIO()

        for chunk in zip_binary.chunks():
            zip_in_ram.write(chunk)

        zip_to_full_dataset(zip_in_ram, self.object)


class DatasetUpdate(
    SuccessMessageMixin, AuthenticatedQuerysetMixin, UpdateView
):
    """Update an existing dataset."""

    model = Dataset
    fields = ["name"]
    template_name = "datasets/edit_dataset.html"
    success_message = "Datensatz erfolgreich bearbeitet."

    def get_unlabeled_count(self):
        """
        Returns the amount of unclassified images of a specific dataset.
        """

        return (
            Dataset.objects.get(id=self.kwargs["pk"])
            .image_set.filter(label__isnull=True)
            .count()
        )

    def get_unlabeled_images(self):
        """
        Returns the unclassified images of a \
        specific dataset as an Image object. \
        """

        return Dataset.objects.get(id=self.kwargs["pk"]).image_set.filter(
            label__isnull=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unlabeled_count"] = self.get_unlabeled_count()
        context["unlabeled_images"] = self.get_unlabeled_images()
        context["dataset_id"] = self.kwargs["pk"]
        context["labels"] = Label.objects.filter(dataset=self.kwargs["pk"])
        context["classify_form"] = DatasetClassifyForm()

        return context


class DatasetClassify(FormView):
    """ Classifies unlabeled images of an existing dataset. """

    form_class = DatasetClassifyForm
    template_name = "datasets/partials/dataset_classify_form.html"
    model = Image

    def set_label(self, image_id, label_id):
        """ Classifiy an image with an specific label. """

        Image.objects.filter(pk=image_id).update(label=label_id)

    def remove_label(self, image_id):
        """ Removes a label of a given image. """

        Image.objects.filter(pk=image_id).update(label=None)

    def form_invalid(self, form):
        """Handling request of invalid form.
        Occurs if the given id is invalid.

        Used for label deletion.
        """
        redirect = HttpResponseRedirect(
            reverse("dataset-edit", kwargs=self.kwargs)
        )

        if "id" not in form.data:
            return redirect

        image_ids = form.data.getlist("image_id_list")

        for image in image_ids:
            self.remove_label(image)

        messages.success(
            self.request, "Bild erfolgreich aus der Klasse gelöscht."
        )

        return redirect

    def form_valid(self, form):
        """Handling request of valid form.
        Occurs if the user want to label images.
        """

        image_ids = form.data.getlist("image_id_list")
        label_id = form.data["label"]

        for image in image_ids:
            self.set_label(image, label_id)

        messages.success(self.request, "Klasse erfolgreich zugeordnet.")

        return HttpResponseRedirect(
            reverse("dataset-edit", kwargs=self.kwargs)
        )


class DatasetDelete(AuthenticatedQuerysetMixin, DeleteView):
    """Delete an existing dataset."""

    model = Dataset
    success_url = reverse_lazy("dataset-list")
    template_name = "datasets/delete_dataset.html"

    def delete(self, request, *args, **kwargs):
        dataset = self.get_object()
        shutil.rmtree(dataset.dir)

        messages.success(self.request, "Datensatz erfolgreich gelöscht.")

        return super().delete(request, args, kwargs)
