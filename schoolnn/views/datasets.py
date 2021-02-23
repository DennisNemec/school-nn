"""Contains all HTTP handling having to do with datasets."""
import os
import shutil
import zipfile
import json
from typing import Optional

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
from django.views.generic import ListView, DetailView
from django.db import transaction
from PIL import Image as PIL_Image, ImageOps
from schoolnn.models import Dataset, Label, Image

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


class DatasetList(ListView):
    """Lists datasets."""

    context_object_name = "datasets"
    template_name = "datasets/list.html"

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


class DatasetDetail(DetailView):
    """Show dataset details."""

    model = Dataset
    template_name = "datasets/detail.html"

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


class DatasetCreate(CreateView):
    """Handles creation of datasets."""

    form_class = DatasetCreateForm
    template_name = "datasets/create.html"

    object: Optional[Dataset] = None

    def form_valid(self, form: DatasetCreateForm):
        """Handle committed dataset create form."""
        self.object = form.save()
        if self.object is None:
            raise ValueError("Failed to parse the dataset create form")

        self.handle_upload(self.request.FILES["file"])
        self.create_tags(self.object)

        shutil.rmtree(self.object.extract_dir)
        os.remove(self.object.upload_file)

        return HttpResponseRedirect(self.get_success_url())

    def handle_upload(self, zip_binary):
        """"Unzips uploaded zip."""
        os.makedirs(self.object.extract_dir, exist_ok=True)

        with open(self.object.upload_file, "wb+") as destination:
            for chunk in zip_binary.chunks():
                destination.write(chunk)

        with zipfile.ZipFile(self.object.upload_file, "r") as zip_ref:
            zip_ref.extractall(self.object.extract_dir)

    def create_tags(self, dataset: Dataset):
        """Create labels."""
        os.makedirs(os.path.join(dataset.dir), exist_ok=True)

        for entry in os.scandir(dataset.extract_dir):
            if entry.is_dir():
                label = Label.objects.create(name=entry.name, dataset=dataset)
                self.process_images(entry, label, dataset)

    @transaction.atomic
    def process_images(
        self, path: os.DirEntry, label: Label, dataset: Dataset
    ):
        """Save images center cropped."""
        for entry in os.scandir(path):
            image = Image.objects.create(dataset=dataset, label=label)
            image_pil = PIL_Image.open(entry.path)
            width, height = image_pil.size
            target_size = min([width, height, 512])
            image_pil = ImageOps.fit(
                image_pil, (target_size, target_size), PIL_Image.ANTIALIAS
            )
            image_pil.save(image.path)


class DatasetUpdate(UpdateView):
    """Update an existing dataset."""

    model = Dataset
    fields = ["name"]
    template_name = "datasets/form.html"

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
    template_name = "datasets/labelform.html"
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

        return redirect

    def form_valid(self, form):
        """Handling request of valid form.
        Occurs if the user want to label images.

        Used for label deletion.
        """

        image_ids = form.data.getlist("image_id_list")
        label_id = form.data["label"]

        for image in image_ids:
            self.set_label(image, label_id)

        return HttpResponseRedirect(
            reverse("dataset-edit", kwargs=self.kwargs)
        )


class DatasetDelete(DeleteView):
    """Delete an existing dataset."""

    model = Dataset
    success_url = reverse_lazy("dataset-list")
    template_name = "datasets/delete.html"
