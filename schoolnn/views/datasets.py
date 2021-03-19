"""Contains all HTTP handling having to do with datasets."""
import shutil
import zipfile
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
            unlabeled_count = Image.objects.filter(
                dataset=dataset, label__isnull=True
            ).count()

            # save dataset specific details to dataset object
            dataset_dict = {}
            dataset_dict["name"] = dataset.name
            dataset_dict["id"] = dataset.id
            dataset_dict["status"] = {
                "is_completely_labeled": unlabeled_count,
                # TODO: add locale
                "text": "Vollständig"
                if unlabeled_count == 0
                else "Unvollständig",
                "background_color": "bg-green"
                if unlabeled_count == 0
                else "bg-yellow",
            }
            dataset_dict["created_at"] = dataset.created_at.strftime(
                "%d.%m.%Y um %H:%M Uhr"
            )

            dataset_list.append(dataset_dict)

        return [listing_type, dataset_list]


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


class DatasetClassify(FormView):
    """ Classifies unlabeled images of an existing dataset. """

    form_class = DatasetClassifyForm
    template_name = "datasets/dataset_label_unlabelled.html"
    model = Image

    def set_label(self, image_id, label_id):
        """ Classifiy an image with an specific label. """

        Image.objects.filter(pk=image_id).update(label=label_id)

    def form_valid(self, form):
        """Handling request of valid form.
        Occurs if the user want to label images.
        """

        image_ids = form.data.getlist("image_id_list")
        label_id = form.data["label"]

        for image in image_ids:
            self.set_label(image, label_id)

        count = len(image_ids)
        label_name = Label.objects.get(id=label_id).name
        image_word = "Bild" if count == 1 else "Bilder"

        messages.success(
            self.request,
            f"{count} {image_word} erfolgreich der Klasse „{label_name}“ "
            f"zugeordnet.",
        )

        return HttpResponseRedirect(
            reverse("dataset-labeleditor", kwargs=self.kwargs)
        )

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

        context["unlabeled_images"] = self.get_unlabeled_images()
        context["unlabeled_count"] = self.get_unlabeled_count()
        context["dataset"] = Dataset.objects.get(id=self.kwargs["pk"])
        context["labels"] = Label.objects.filter(dataset=self.kwargs["pk"])

        return context


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
